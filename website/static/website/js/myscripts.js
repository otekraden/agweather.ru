function forecastChart(chartjs_data, chartjs_options) {

    const ctx = document.getElementById('myAreaChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: chartjs_data,

        options: {
            interaction: {
                intersect: false,
                mode: 'index',
            },
            spanGaps: true,
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 16
                        },
                        color: '#FFFFFF',
                        padding: 20,
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            let index = tooltipItems[0].dataIndex;
                            return chartjs_options['tooltip_titles'][index];
                        },
                    }
                }
            },
            scales: {
                x: {
                    border: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: chartjs_options['last_database_refresh'],
                        color: '#FFFFFF',
                        font: {
                            size: 14,
                        },
                        align: 'start',
                        padding: 10,
                    },
                    grid: {
                        color: function (context) {
                            if (context.tick.label == ' ') {
                                return '#555555';
                            }
                            return '#111111';
                        },
                    },
                    ticks: {
                        color: function (context) {
                            if (context.tick.label == 'Sun' || context.tick.label == 'Sat') {
                                return '#FF0000';
                            }
                            return '#FFFFFF';
                        },
                        font: {
                            size: 14,
                            weight: function (context) {
                                if (context.tick.label == 'Sun' || context.tick.label == 'Sat') {
                                    return 'bold';
                                }
                                return 'normal';
                            },
                        },
                        // display: true,
                        autoSkip: false,
                        maxRotation: 0,
                        // major: {
                        //   enabled: true
                        // },
                    }
                },
                y: {
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: weather_parameter.value,
                        color: '#FFFFFF',
                        font: {
                            size: 18,
                        },
                    },
                    suggestedMin: chartjs_options['suggestedMin'],
                    suggestedMax: chartjs_options['suggestedMax'],
                    grid: {
                        color: function (context) {
                            if (context.tick.value == 0 || context.tick.value == 760) {
                                return '#FFFFFF';
                            } else {
                                return '#222111';
                            }

                        },
                    },
                    ticks: {
                        color: '#FFFFFF',
                        font: {
                            size: 14
                        },
                    }
                }
            }
        }
    });
}

function archiveChart(chartjs_data, chartjs_options) {

    const ctx = document.getElementById('myAreaChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: chartjs_data,

        options: {
            interaction: {
                intersect: false,
                mode: 'index',
            },
            spanGaps: true,
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 16
                        },
                        color: '#FFFFFF',
                        padding: 20,
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            let index = tooltipItems[0].dataIndex;
                            return chartjs_options['tooltip_titles'][index];
                        },
                    }
                }
            },
            scales: {
                x: {
                    border: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: chartjs_options['last_database_refresh'],
                        color: '#FFFFFF',
                        font: {
                            size: 14,
                        },
                        align: 'end',
                        padding: 10,
                    },
                    grid: {
                        color: function (context) {
                            if (context.tick.label == ' ') {
                                return '#555555';
                            }
                            return '#111111';
                        },
                    },
                    ticks: {
                        color: function (context) {
                            if (context.tick.label == 'Sun' || context.tick.label == 'Sat') {
                                return '#FF0000';
                            }
                            return '#FFFFFF';
                        },
                        font: {
                            size: 14,
                            weight: function (context) {
                                if (context.tick.label == 'Sun' || context.tick.label == 'Sat') {
                                    return 'bold';
                                }
                                return 'normal';
                            },
                        },
                        // display: true,
                        autoSkip: false,
                        maxRotation: 0,
                        // major: {
                        //   enabled: true
                        // },
                    }
                },
                y: {
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: weather_parameter.value,
                        color: '#FFFFFF',
                        font: {
                            size: 18,
                        },
                    },
                    suggestedMin: chartjs_options['suggestedMin'],
                    suggestedMax: chartjs_options['suggestedMax'],
                    grid: {
                        color: function (context) {
                            if (context.tick.value == 0 || context.tick.value == 760) {
                                return '#FFFFFF';
                            } else {
                                return '#222111';
                            }

                        },
                    },
                    ticks: {
                        color: '#FFFFFF',
                        font: {
                            size: 14
                        },
                    }
                }
            }
        }
    });
}
