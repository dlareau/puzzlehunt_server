google.load('visualization', '1', {packages: ['corechart', 'bar']});
google.setOnLoadCallback(drawStacked);

function drawStacked() {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Puzzle Name');
  data.addColumn('number', 'Solved');
  data.addColumn('number', 'Unlocked');
  data.addColumn('number', 'Locked');

  data.addRows([
    {% for point in data1_list %}
      ["{{point.name}}", {{point.solved}}, {{point.unlocked}}, {{point.locked}}],
    {% endfor %}
  ]);

  var options = {
    title: 'Puzzle solves',
    isStacked: true,
    height: 400,
    width: 800,
    chartArea: {
       top: 20,
       left: 50,
       height: '50%'
    },
    hAxis: {slantedText:true, slantedTextAngle:60 },
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
  chart.draw(data, options);
}