# Time_Keeper
Tracks your time, works with a MySQL database to store and retrieve time information

<img width="398" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/def4d6a1-2886-4b1d-89fc-e4de1dcbb0b5">

<img width="398" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/ce878513-dade-4c97-aae4-d53ee06c45a4">

<img width="396" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/bba2285f-cacc-4362-a2e6-117eda7772f7">

<div id="data"></div>
<script>
fetch('https://proficientpc.com/time_keeper_tasks.php')
    .then(response => response.json())
    .then(data => {
        // The 'data' variable contains the JSON data from your PHP script.
        // You can now extract the specific information you want.
        const widget = document.querySelector('#data');
        let output = '';
        for (let task of data) {
            output += `Name: ${task.task_name}, Start time: ${task.start_time},
                End time: ${task.end_time},
                Duration: ${task.duration}<br>`;
        }
        widget.innerHTML = output;
    })
    .catch(error => console.error('Error:', error));

</script>
