$(document).ready(function () {
    function updateGraphs() {
        const hostname = $('#hostname').val();
        const startDate = $('#start_date').val();
        const endDate = $('#end_date').val();

        $.post('/update_graphs', {
            hostname: hostname,
            start_date: startDate,
            end_date: endDate
        }, function (data) {
            Plotly.react('cpu-usage', JSON.parse(data.graph_cpu).data, JSON.parse(data.graph_cpu).layout);
            Plotly.react('memory-usage', JSON.parse(data.graph_memory).data, JSON.parse(data.graph_memory).layout);
            Plotly.react('network-traffic', JSON.parse(data.graph_network).data, JSON.parse(data.graph_network).layout);
        });
    }

    $('#update-btn').click(function () {
        updateGraphs();
    });

    setInterval(updateGraphs, 30000); // Atualizar a cada 30 segundos
});
