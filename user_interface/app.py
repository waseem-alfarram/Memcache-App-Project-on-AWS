from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.utils import secure_filename
from cache import Cache
from time import perf_counter
from datetime import datetime
import os, threading
import boto3


UPLOAD_FOLDER = 'static/destination_images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'memcache-database.cz0uhkdlsnct.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'Memcache_Database'
app.secret_key = "my-secret-key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mysql = MySQL(app)
s3 = boto3.client("s3")
autoscaling = boto3.client('autoscaling')
cloudwatch = boto3.client('cloudwatch')
cache = Cache(500, "random-replacement")
hitsNo = 0
missNo = 0
reqs = 0


def updateRecord():
    global hitsNo, missNo, reqs
    hitRate = 0
    missRate = 0
    asg_dict = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=['memcache-asg'])
    asg_capacity = asg_dict["AutoScalingGroups"][0]['DesiredCapacity']
    if reqs !=0 :
        hitRate = (hitsNo/reqs)*100
        missRate = (missNo/reqs)*100
        cloudwatch.put_metric_data(Namespace = 'MissRate', MetricData = [{'MetricName': 'MissRateMetric', 'Value': missRate}])
        cloudwatch.put_metric_data(Namespace = 'HitRate', MetricData = [{'MetricName': 'HitRateMetric', 'Value': hitRate}])
    cloudwatch.put_metric_data(Namespace = 'Workers', MetricData = [{'MetricName': 'WorkersMetric', 'Value': asg_capacity}])
    cloudwatch.put_metric_data(Namespace = 'ItemsNumber', MetricData = [{'MetricName': 'ItemsNumberMetric', 'Value': cache.length()}])
    cloudwatch.put_metric_data(Namespace = 'ItemsSize', MetricData = [{'MetricName': 'ItemsSizeMetric', 'Value': cache.size()}])
    cloudwatch.put_metric_data(Namespace = 'RequestsNumber', MetricData = [{'MetricName': 'RequestsNumberMetric', 'Value': reqs}])

    hitsNo = 0
    missNo = 0
    reqs = 0


def counter():
    t1_start = perf_counter()
    send = True
    while True:
        now = perf_counter()
        if (int(now)-int(t1_start)) % 5 == 0 and send:
            updateRecord()
            send = False
        elif (int(now)-int(t1_start)) % 5 != 0:
            send = True


t1 = threading.Thread(daemon=True, target=counter, args=())
t1.start()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['POST', 'GET'])
@app.route("/add_image/", methods=['POST', 'GET'])
def add_image():
    global cache
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image_key FROM image")
    keys = cursor.fetchall()
    if len(keys) == 0:
        list = os.listdir('static/destination_images/')
        for file in list:
            if os.path.exists('static/destination_images/'):
                os.remove('static/destination_images/' + file)
    cursor.execute("SELECT capacity FROM memory_configuration WHERE seq = 1")
    capacity = int(cursor.fetchone()[0])
    cursor.execute("SELECT replacement_policy FROM memory_configuration WHERE seq = 1")
    replacement_policy = cursor.fetchone()
    cache = Cache(capacity, replacement_policy)
    if request.method == 'POST':
        my_key = request.form['key']
        name = request.files['name']
        if name and allowed_file(name.filename):
            filename = secure_filename(name.filename)
            cursor.execute("SELECT image_key FROM image")
            keys = cursor.fetchall()
            key_exist = 'false'
            for key in keys:
                if int(my_key) == int(key[0]):
                    key_exist = 'true'
                    break
            if key_exist == 'false':
                name.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                s3.upload_file(Filename="static/destination_images/"+filename, Bucket="memcache-cloud-bucket", Key=filename)
                cursor.execute("INSERT INTO image(image_key, image_name, size) VALUES(%s, %s, %s)", (my_key, name.filename, img_size))
                flash('Image is successfully uploaded!')
            else:
                if my_key in cache.data:
                    cache.invalidateKey(my_key)
                cursor.execute("SELECT image_name FROM image WHERE image_key=%s", [my_key])
                filename2 = cursor.fetchone()
                s3.delete_object(Bucket="memcache-cloud-bucket", Key=filename2[0])
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], filename2[0]))
                cursor.execute("DELETE FROM image WHERE image_key=%s", [my_key])
                name.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute("INSERT INTO image(image_key, image_name, size) VALUES(%s, %s, %s)", (my_key, name.filename, img_size))
                s3.upload_file(Filename="static/destination_images/"+filename, Bucket="memcache-cloud-bucket", Key=filename)
                flash('Image is successfully updated!')
        else:
            flash('(png, jpg, jpeg, gif) files only!')
    mysql.connection.commit()
    cursor.close()
    return render_template("add_image.html")


@app.route("/show_image/", methods=['POST', 'GET'])
def show_image():
    global hitsNo, missNo, reqs
    reqs += 1
    img_src = '/static/temp.jpg'
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT clear_cache FROM memory_configuration WHERE seq = 1")
    clear_cache = cursor.fetchone()
    if clear_cache[0] == 'yes':
        cache.clear()
    cursor.execute("SELECT image_key FROM image")
    keys = cursor.fetchall()
    if len(keys) == 0:
        list = os.listdir('static/destination_images/')
        for file in list:
            if os.path.exists('static/destination_images/'):
                os.remove('static/destination_images/' + file)
    if request.method == 'POST':
        key = int(request.form['key'])
        cursor.execute("SELECT image_name FROM image WHERE image_key = %s", [key])
        file = cursor.fetchone()
        if key in cache.data:
            hitsNo += 1
            [src, ext] = cache.get(key)
            img_src = "data:image/+" + ext + ";base64," + src.decode()
        else:
            if file:
                filename = secure_filename(file[0])
                s3.download_file(Bucket="memcache-cloud-bucket", Key=filename, Filename="static/destination_images/"+filename)
                cache.put(int(key), filename)
                img_src = '/' + os.path.join(app.config['UPLOAD_FOLDER'], filename)
                flash('Image is successfully retrieved!')
            else:
                missNo += 1
    mysql.connection.commit()
    cursor.close()
    return render_template("show_image.html", image_src = img_src)


@app.route("/show_keys/", methods=['POST', 'GET'])
def show_keys():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image_key FROM image")
    keys = cursor.fetchall()
    if len(keys) == 0:
        list = os.listdir('static/destination_images/')
        for file in list:
            if os.path.exists('static/destination_images/'):
                os.remove('static/destination_images/' + file)
    if request.method == 'GET':
        cursor.execute("SELECT image_key FROM image ORDER BY image_key ASC")
        keys = cursor.fetchall()
        for key in keys:
            flash(key[0])
    mysql.connection.commit()
    cursor.close()
    return render_template("show_keys.html")


app.run(host='0.0.0.0', port=5000, debug=True)
