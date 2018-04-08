google.load('visualization', '1', {packages: ['corechart', 'bar']});
google.setOnLoadCallback(drawStacked);

function drawStacked() {

  // Chart 1
  var data1 = new google.visualization.DataTable();
  data1.addColumn('string', 'Puzzle Name');
  data1.addColumn('number', 'Solved');
  data1.addColumn('number', 'Unlocked');
  data1.addColumn('number', 'Locked');

  data1.addRows([
    {% for point in data1_list %}
      ["{{point.name}}", {{point.solved}}, {{point.unlocked}}, {{point.locked}}],
    {% endfor %}
  ]);

  var options1 = {
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

  var chart1 = new google.visualization.ColumnChart(document.getElementById('chart_div1'));
  chart1.draw(data1, options1);


  // Chart 2
  var data2 = new google.visualization.DataTable();
  data2.addColumn('string', 'Puzzle Name');
  data2.addColumn('number', 'Correct submissions');
  data2.addColumn('number', 'Incorrect submissions');

  data2.addRows([
    {% for point in data2_list %}
      ["{{point.name}}", {{point.correct}}, -{{point.incorrect}}],
    {% endfor %}
  ]);

  var options2 = {
    title: 'Puzzle submissions',
    isStacked: true,
    height: 600,
    width: 800,
    chartArea: {
       top: 20,
       left: 50,
       height: '50%'
    },
    hAxis: {slantedText:true, slantedTextAngle:60 },
  };

  var chart2 = new google.visualization.ColumnChart(document.getElementById('chart_div2'));
  chart2.draw(data2, options2);


  // Chart 3
  var data3 = new google.visualization.DataTable();
  data3.addColumn('string', 'Hour');
  data3.addColumn('number', 'amount');

  data3.addRows([
    {% for point in data3_list %}
      ["{{point.hour}}", {{point.amount}}],
    {% endfor %}
  ]);

  var options3 = {
    title: 'Submissions over time',
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

  var chart3 = new google.visualization.ColumnChart(document.getElementById('chart_div3'));
  chart3.draw(data3, options3);


  // Chart 4
  var data4 = new google.visualization.DataTable();
  data4.addColumn('string', 'Hour');
  data4.addColumn('number', 'amount');

  data4.addRows([
    {% for point in data4_list %}
      ["{{point.hour}}", {{point.amount}}],
    {% endfor %}
  ]);

  var options4 = {
    title: 'Solves over time',
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

  var chart4 = new google.visualization.ColumnChart(document.getElementById('chart_div4'));
  chart4.draw(data4, options4);


  // Chart 5
  var data5 = new google.visualization.DataTable();
  data5.addColumn('datetime', 'Time');
  {% for team in teams %}
    data5.addColumn('number', "{{team.team_name}} Solves");
  {% endfor %}


  data5.addRows([
    {% for line in data5_list %}
      [
        {% for point in line %}
          {% if forloop.first %}
            new Date("{{ point.isoformat }}"),
          {% else %}
            {{point|safe}},
          {% endif %}
        {% endfor %}
      ],
    {% endfor %}
  ]);

  var options5 = {
    title: 'Solves by team over time',
    height: 1000,
    width: 1200,
    chartArea: {
       top: 20,
       left: 50,
       height: '50%'
    },
    vAxis: {maxValue: {{num_puzzles}}},
    hAxis: {slantedText:true, slantedTextAngle:60 },
  };

  var chart5 = new google.visualization.LineChart(document.getElementById('chart_div5'));
  chart5.draw(data5, options5);
}
