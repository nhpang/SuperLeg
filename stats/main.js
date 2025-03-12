fetchedData = {}

async function search(input){
  document.getElementById('intro').style.display='none';
  document.getElementById('error').style.display='none';
  document.getElementById('loading').style.display='block';
    console.log("Data updated:", fetchedData);
    try {
      const response = await fetch('http://localhost:420/stats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "name": input
        })
      })
  
      if (!response.ok) {
        document.getElementById('loading').style.display='none';
        document.getElementById('error').style.display='block';
        throw new Error("Failed to update data");
      }
  
      fetchedData = await response.json();
      console.log("Data updated:", fetchedData);
      
      
      populate(fetchedData)
      document.getElementById('loading').style.display='none';
    } catch (error) {
      console.error("Error fetching data:", error);
    }
}

function populate(fetchedData){
  const image = document.querySelector('.left1');
  image.innerHTML = ''; 

  // const textpart = document.querySelector('.about');
  // textpart.innerHTML = ''; 

  const name = document.querySelector('.left1');
  name.innerHTML = ''; 

  const tabledata = document.querySelector('.left2');
  tabledata.innerHTML = ''; 

  const averages = document.querySelector('.up');
  averages.innerHTML = ''; 

  const predictions = document.querySelector('.down');
  predictions.innerHTML = ''; 

  

  image.innerHTML += fetchedData['image'];

  image.innerHTML += '<div style="margin-left: 15px; margin-top: 15px"><h1>'+fetchedData['player'].split('2')[0]+'</h1><p>'+fetchedData['accolades']+'</p></div>'
  
  tabledata.innerHTML += '<table id="csv-table" border="1"></table>';

  averages.innerHTML += '<h1>Averages over Last 2 Years</h1>';
  for (let i of fetchedData['average']) {
    averages.innerHTML += '<h2>'+i+'</h2>';
  }

  predictions.innerHTML += '<h1>Next Game Predictions</h1>';
  for (let i of fetchedData['prediction']) {
    predictions.innerHTML += '<h2>'+i+'</h2>';
  }
  function createCSVTable(fetchedData) {
    const table = document.getElementById('csv-table');

    table.innerHTML = '';

    const rows = fetchedData['game'].split('\n');

    rows.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');

        const cells = row.split(',');

        cells.forEach((cell, cellIndex) => {
            const td = document.createElement(rowIndex === 0 ? 'th' : 'td');

            td.textContent = cell.trim();

            tr.appendChild(td);
        });

        table.appendChild(tr);
    });
}

  createCSVTable(fetchedData);
}