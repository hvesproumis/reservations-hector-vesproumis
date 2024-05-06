function fetchAndDisplayChart(){

    

    function display(container_name){
        $.ajax({
            url: $("#" + container_name).attr("data-url"),
            dataType: 'json',
            success: function (data) {
            Highcharts.chart(container_name, data);
            }
        });
    }
}