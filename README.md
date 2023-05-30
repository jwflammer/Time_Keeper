<h1>Time Keeper</h1>

<p>Time Keeper is a task time tracker application. It allows users to track the time they spend on different tasks and stores this data in a MySQL database.</p>

<img width="398" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/def4d6a1-2886-4b1d-89fc-e4de1dcbb0b5">

<img width="398" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/ce878513-dade-4c97-aae4-d53ee06c45a4">

<img width="396" alt="image" src="https://github.com/jwflammer/Time_Keeper/assets/23066085/bba2285f-cacc-4362-a2e6-117eda7772f7">

<h2>Features</h2>

<ul>
  <li>Start and stop a timer for each task.</li>
  <li>Display the current task and its duration.</li>
  <li>Load tasks and their durations from a MySQL database.</li>
  <li>Store the start time of a task in the database.</li>
  <li>User-friendly interface built with PyQt5.</li>
</ul>

<h2>Getting Started</h2>

<h3>Prerequisites</h3>

<p>Before you begin, ensure you have met the following requirements:</p>

<ul>
  <li>You have installed the latest version of Python and PyQt5.</li>
  <li>You have a MySQL server running.</li>
</ul>

<h3>Installing Time Keeper</h3>

<p>To install Time Keeper, follow these steps:</p>

<ol>
  <li>Clone the repository:</li>
</ol>

<pre>
<code>
git clone https://github.com/jwflammer/Time_Keeper.git
</code>
</pre>

<ol start="2">
  <li>Navigate to the cloned repository:</li>
</ol>

<pre>
<code>
cd Time_Keeper
</code>
</pre>

<ol start="3">
  <li>Install the required Python packages:</li>
</ol>

<pre>
<code>
pip install -r requirements.txt
</code>
</pre>

<h2>Database Setup</h2>

<p>Time Keeper uses a MySQL database to store task information. Here's how to set it up:</p>

<ol>
  <li>Install MySQL Server if you haven't done so already.</li>
  <li>Create a new database named <code>time_keeper_db</code>:</li>
</ol>

<pre>
<code>
CREATE DATABASE time_keeper_db;
</code>
</pre>

<ol start="2">
  <li>Select the new database:</li>
</ol>

<pre>
<code>
USE time_keeper_db;
</code>
</pre>

<ol start="3">
  <li>Create a new table named <code>tasks</code> with the following schema:</li>
</ol>

<pre>
<code>
CREATE TABLE tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task_name VARCHAR(255) NOT NULL,
  start_time TIMESTAMP,
  duration INT
);
</code>
</pre>

<p>Please replace <code>time_keeper_db</code> and <code>tasks</code> with your actual database and table names if they are different.</p>

<h3>Database Configuration in Application</h3>

<p>In your Python script, make sure to configure the database connection with your MySQL server details:</p>

<pre>
<code>
config = {
  'user': 'your_username',
  'password': 'your_password',
  'host': 'localhost',
  'database': 'time_keeper_db',
  'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
</code>
</pre>

<p>Replace <code>your_username</code> and <code>your_password</code> with your MySQL server username and password.</p>

<h3>Using Time Keeper</h3>

<p>To use Time Keeper, follow these steps:</p>

<ol>
  <li>Run the script:</li>
</ol>

<pre>
<code>
python main.py
</code>
</pre>

<ol start="4">
  <li>Use the interface to start and stop tasks.</li>
</ol>

<h2>Contributing to Time Keeper</h2>

<p>To contribute to Time Keeper, follow these steps:</p>

<ol>
  <li>Fork this repository.</li>
  <li>Create a branch: <code>git checkout -b &lt;branch_name&gt;</code></li>
  <li>Make your changes and commit them: <code>git commit -m '&lt;commit_message&gt;'</code></li>
  <li>Push to the original branch: <code>git push origin &lt;project_name&gt;/&lt;location&gt;</code></li>
  <li>Create the pull request.</li>
</ol>

<h2>Contact</h2>

<p>If you want to contact me you can reach me at &lt;johnf@proficientpc.com&gt;.</p>
