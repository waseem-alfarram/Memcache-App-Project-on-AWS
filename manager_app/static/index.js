const workers = document.getElementById('workers');
const miss_rate = document.getElementById('miss_rate');
const hit_rate = document.getElementById('hit_rate');
const items_number = document.getElementById('items_number');
const items_size = document.getElementById('items_size');
const requests_number = document.getElementById('requests_number');


const labels_values = [...Array(30).keys()].map(i => i + 1);
const workers_data = JSON.parse(document.getElementById('workers_metric').innerHTML);
const miss_rate_data = JSON.parse(document.getElementById('miss_rate_metric').innerHTML);
const hit_rate_data = JSON.parse(document.getElementById('hit_rate_metric').innerHTML);
const items_number_data = JSON.parse(document.getElementById('items_number_metric').innerHTML);
const items_size_data = JSON.parse(document.getElementById('items_size_metric').innerHTML);
const requests_data = JSON.parse(document.getElementById('requests_metric').innerHTML);


new Chart(workers, {
    type: 'bar',
    data: {
        labels: labels_values,
        datasets: [{
            label: "Workers No.",
            data: workers_data,
            backgroundColor: [
                'rgb(247, 0, 0)',
            ],
            borderColor: [
                'rgb(54, 162, 245)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 10
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "workers",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 8,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
});

new Chart(miss_rate, {
    type: 'line',
    data: {
        labels: labels_values,
        datasets: [{
            label: 'Miss Rate',
            data: miss_rate_data,
            fill: true,
            borderColor: 'rgb(0, 154, 22)',
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 2,
            pointHoverRadius: 4
        }]
    },
    options: {
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 10
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "miss rate",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 100,
                ticks: {
                    stepSize: 10
                }
            }
        }
    }
});


new Chart(hit_rate, {
    type: 'line',
    data: {
        labels: labels_values,
        datasets: [{
            label: 'Hit Rate',
            data: hit_rate_data,
            fill: true,
            borderColor: 'rgb(255, 102, 0)',
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 2,
            pointHoverRadius: 4
        }]
    },
    options: {
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 10
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "hit rate",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 100,
                ticks: {
                    stepSize: 10
                }
            }
        }
    }
});


new Chart(items_number, {
    type: 'bar',
    data: {
        labels: labels_values,
        datasets: [{
            label: "Items No.",
            data: items_number_data,
            backgroundColor: [
                'rgb(0, 140, 227)',
            ],
            borderColor: [
                'rgb(255, 99, 132)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 10
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "items no.",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 10,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
});


new Chart(items_size, {
    type: 'line',
    data: {
        labels: labels_values,
        datasets: [{
            label: 'Items Size',
            data: items_size_data,
            fill: true,
            borderColor: 'rgb(160, 32, 240)',
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 2,
            pointHoverRadius: 4
        }]
    },
    options: {
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 9
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "items size (KB)",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 1000,
                ticks: {
                    stepSize: 100
                }
            }
        }
    }
});


new Chart(requests_number, {
    type: 'bar',
    data: {
        labels: labels_values,
        datasets: [{
            label: "Requests No.",
            data: requests_data,
            backgroundColor: [
                'rgb(236, 198, 100)',
            ],
            borderColor: [
                'rgb(255, 99, 132)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: "minutes",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        size: 9
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: "requests no.",
                    font: {
                        size: 15,
                        weight: "bold"
                    }
                },
                suggestedMin: 0,
                suggestedMax: 40,
                ticks: {
                    stepSize: 5
                }
            }
        }
    }
});


function generate_workers() {
    const arr = new Array(30).fill(null).map(() => Math.floor(1.0 + Math.random() * 8))
    return arr
}


function generate_miss_hit_rate() {
    const arr = new Array(30).fill(null).map(() => (Math.random() * 100))
    return arr
}


function generate_items_no() {
    const arr = new Array(30).fill(null).map(() => Math.floor(Math.random() * 11))
    return arr
}


function generate_items_size() {
    const arr = new Array(30).fill(null).map(() => Math.floor(Math.random() * 1001))
    return arr
}


function generate_requests_no() {
    const arr = new Array(30).fill(null).map(() => Math.floor(Math.random() * 401))
    return arr
}
