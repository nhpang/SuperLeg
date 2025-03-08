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

  const name = document.querySelector('.left1');
  name.innerHTML = ''; 

  const tabledata = document.querySelector('.left2');
  tabledata.innerHTML = ''; 

  const averages = document.querySelector('.up');
  averages.innerHTML = ''; 

  const predictions = document.querySelector('.down');
  predictions.innerHTML = ''; 

  

  image.innerHTML += fetchedData['image'];
  name.innerHTML += '<h1>'+fetchedData['player'].split('2')[0]+'</h1>'
  
  tabledata.innerHTML += '<table id="csv-table" border="1"></table>';

  averages.innerHTML += '<h1>Averages on Recent Games</h1>';
  for (let i of fetchedData['average']) {
    averages.innerHTML += '<h2>'+i+'</h2>';
  }

  predictions.innerHTML += '<h1>Next Game predictions</h1>';
  for (let i of fetchedData['prediction']) {
    predictions.innerHTML += '<h2>'+i+'</h2>';
  }
  function createCSVTable(fetchedData) {
    // Get the table element
    const table = document.getElementById('csv-table');

    // Clear any existing content in the table
    table.innerHTML = '';

    // Split the CSV data into rows
    const rows = fetchedData['game'].split('\n');

    // Loop through each row
    rows.forEach((row, rowIndex) => {
        // Create a new table row
        const tr = document.createElement('tr');

        // Split the row into cells
        const cells = row.split(',');

        // Loop through each cell
        cells.forEach((cell, cellIndex) => {
            // Create a new table cell
            const td = document.createElement(rowIndex === 0 ? 'th' : 'td'); // Use <th> for the header row

            // Set the cell's text content
            td.textContent = cell.trim();

            // Append the cell to the row
            tr.appendChild(td);
        });

        // Append the row to the table
        table.appendChild(tr);
    });
}

  createCSVTable(fetchedData);
}
