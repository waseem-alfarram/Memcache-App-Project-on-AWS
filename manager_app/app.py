import threading
from time import perf_counter
from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
from datetime import datetime
from cache import Cache
from datetime import datetime, timedelta
import boto3


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'memcache-database.cz0uhkdlsnct.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'Memcache_Database'
app.secret_key = "my-secret-key"


mysql = MySQL(app)
s3 = boto3.resource("s3")
autoscaling = boto3.client('autoscaling')
cloudwatch = boto3.client('cloudwatch')
cache = Cache(500, "random-replacement")
workers_metric = []
missRate_metric = []
hitRate_metric = []
itemsNumber_metric = []
itemsSize_metric = []
requests_metric = []


def update_metric_data():
    start_time = datetime.utcnow() - timedelta(seconds=60)
    end_time = datetime.utcnow()
    missRate_params = {
        'Namespace': 'MissRate',
        'MetricName': 'MissRateMetric',
        'StartTime': start_time,
        'EndTime': end_time,
        'Period': 60,
        'Statistics': ['Average']
    }
    hitRate_params = {
        'Namespace': 'HitRate',
        'MetricName': 'HitRateMetric',
        'StartTime': start_time,
        'EndTime': end_time,
        'Period': 60,
        'Statistics': ['Average']
    }
    itemsNumber_params = {
        'Namespace': 'ItemsNumber',
        'MetricName': 'ItemsNumberMetric',
        'StartTime': start_time,
        'EndTime': end_time,
        'Period': 60,
        'Statistics': ['Maximum']
    }
    itemsSize_params = {
        'Namespace': 'ItemsSize',
        'MetricName': 'ItemsSizeMetric',
        'StartTime': start_time,
        'EndTime': end_time,
        'Period': 60,
        'Statistics': ['Maximum']
    }
    requests_params = {
        'Namespace': 'RequestsNumber',
        'MetricName': 'RequestsNumberMetric',
        'StartTime': start_time,
        'EndTime': end_time,
        'Period': 60,
        'Statistics': ['Sum']
    }
    
    missRate_response = cloudwatch.get_metric_statistics(**missRate_params)
    hitRate_response = cloudwatch.get_metric_statistics(**hitRate_params)
    itemsNumber_response = cloudwatch.get_metric_statistics(**itemsNumber_params)
    itemsSize_response = cloudwatch.get_metric_statistics(**itemsSize_params)
    requests_response = cloudwatch.get_metric_statistics(**requests_params)
    
    if len(workers_metric) == 30:
        workers_metric.pop(0)
    if len(missRate_metric) == 30:
        missRate_metric.pop(0)
    if len(hitRate_metric) == 30:
        hitRate_metric.pop(0)
    if len(itemsNumber_metric) == 30:
        itemsNumber_metric.pop(0)
    if len(itemsSize_metric) == 30:
        itemsSize_metric.pop(0)
    if len(requests_metric) == 30:
        requests_metric.pop(0)
    
    asg_dict = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=['memcache-asg'])
    workers_data_point = asg_dict["AutoScalingGroups"][0]['DesiredCapacity']
    workers_metric.append(workers_data_point)
    if len(missRate_response['Datapoints']) != 0:
        missRate_data_point = missRate_response['Datapoints'][0]['Average']
        missRate_metric.append(missRate_data_point)
    if len(hitRate_response['Datapoints']) != 0:
        hitRate_data_point = hitRate_response['Datapoints'][0]['Average']
        hitRate_metric.append(hitRate_data_point)
    if len(itemsNumber_response['Datapoints']) != 0:
        itemsNumber_data_point = itemsNumber_response['Datapoints'][0]['Maximum']
        itemsNumber_metric.append(itemsNumber_data_point)
    if len(itemsSize_response['Datapoints']) != 0:
        itemsSize_data_point = itemsSize_response['Datapoints'][0]['Maximum']
        itemsSize_metric.append(itemsSize_data_point)
    if len(requests_response['Datapoints']) != 0:
        requests_data_point = requests_response['Datapoints'][0]['Sum']
        requests_metric.append(requests_data_point)
    
    print("workers_metric is: ", workers_metric)
    print("missRate_metric is: ", missRate_metric)
    print("hitRate_metric is: ", hitRate_metric)
    print("itemsNumber_metric is: ", itemsNumber_metric)
    print("itemsSize_metric is: ", itemsSize_metric)
    print("requests_metric is: ", requests_metric)


def counter():
    t1_start = perf_counter()
    send = True
    while True:
        now = perf_counter()
        if (int(now)-int(t1_start)) % 60 == 0 and send:
            update_metric_data()
            send = False
        elif (int(now)-int(t1_start)) % 60 != 0:
            send = True


t1 = threading.Thread(daemon=True, target=counter, args=())
t1.start()


@app.route("/", methods=['POST', 'GET'])
@app.route("/memory_configuration/", methods=['POST', 'GET'])
def memory_configuration():
    if request.method == 'POST':
        flash_message = 'Memcache Configurations are set successfully!'
        capacity = request.form['capacity']
        if capacity == "":
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT capacity FROM memory_configuration WHERE seq = 1")
            cap = cursor.fetchone()
            capacity = cap[0]
            mysql.connection.commit()
            cursor.close()
        replacement_policy = request.form['replacement-policy']
        memcache_pool_resizing_option = request.form['memcache-pool-resizing-option']
        if memcache_pool_resizing_option == 'manual':
            autoscaling.put_scaling_policy(AutoScalingGroupName = 'memcache-asg', PolicyName = 'Expand-Automatic-Scaling-Policy', Enabled = False, AdjustmentType = 'PercentChangeInCapacity', ScalingAdjustment = 100)
            autoscaling.put_scaling_policy(AutoScalingGroupName = 'memcache-asg', PolicyName = 'Shrink-Automatic-Scaling-Policy', Enabled = False, AdjustmentType = 'PercentChangeInCapacity', ScalingAdjustment = -50)
            pool_size_option = request.form['pool-size-option']
            pool_resize_number = request.form['pool-resize-number']
            if pool_resize_number == "":
                pool_resize_number = 0
            else:
                pool_resize_number = int(pool_resize_number)
            asg_dict = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=['memcache-asg'])
            asg_capacity = asg_dict["AutoScalingGroups"][0]['DesiredCapacity']
            if pool_size_option == 'expand':
                if asg_capacity + pool_resize_number <= 8:
                    autoscaling.set_desired_capacity(AutoScalingGroupName = 'memcache-asg', DesiredCapacity = asg_capacity + pool_resize_number)
                else:
                    flash_message = 'Failed! Expanded Capacity is greater than 8'
            else:
                if asg_capacity - pool_resize_number >= 1:
                    autoscaling.set_desired_capacity(AutoScalingGroupName = 'memcache-asg', DesiredCapacity = asg_capacity - pool_resize_number)
                else:
                    flash_message = 'Failed! Shrinked Capacity is less than 1'
        else:
            autoscaling.put_scaling_policy(AutoScalingGroupName = 'memcache-asg', PolicyName = 'Expand-Automatic-Scaling-Policy', Enabled = True, PolicyType = 'SimpleScaling', AdjustmentType = 'PercentChangeInCapacity', ScalingAdjustment = 100)
            autoscaling.put_scaling_policy(AutoScalingGroupName = 'memcache-asg', PolicyName = 'Shrink-Automatic-Scaling-Policy', Enabled = True, PolicyType = 'SimpleScaling', AdjustmentType = 'PercentChangeInCapacity', ScalingAdjustment = -50)
        clear_cache = request.form['clear-cache']
        delete_application_data = request.form['delete-application-data']
        cursor = mysql.connection.cursor()
        if delete_application_data == 'yes':
            cursor.execute("DELETE FROM image")
            bucket = s3.Bucket('memcache-cloud-bucket')
            bucket.objects.all().delete()
        if clear_cache == 'yes':
            cache.clear()
        cursor.execute("UPDATE memory_configuration SET capacity = %s, replacement_policy = %s, clear_cache = %s WHERE seq = 1", (capacity, replacement_policy, clear_cache))
        mysql.connection.commit()
        cursor.close()
        cache.refreshConfiguration(int(capacity), replacement_policy)
        flash(flash_message)
    return render_template("memory_configuration.html")


@app.route("/memory_statistics/")
def memory_statistics():
    global workers_metric, missRate_metric, hitRate_metric, itemsNumber_metric, itemsSize_metric, requests_metric
    return render_template("memory_statistics.html", workers = workers_metric, miss_rate = missRate_metric, hit_rate = hitRate_metric, items_number = itemsNumber_metric, items_size = itemsSize_metric, requests = requests_metric)


app.run(host='0.0.0.0', port=5000, debug=True)
