import './App.css';
import React, {useState, useEffect} from 'react';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [jobs, setSearchJobs] = useState([]);

  const fetchJobs = async (query) => {
    try {
      const response = await fetch(`http://localhost:8000/job/${query}`);
      const data = await response.json();
      setSearchJobs(data)
      console.log(data);
    } catch (error) {
      console.error('Error:',error);
    }
  }
      
  useEffect(() => {
    fetchJobs('');
  }, []);

  const handleChange = (event) => {
    setSearchTerm(event.target.value);
    const query = event.target.value.trim()
    if (query.length >= 3) {
      fetchJobs(query);
    } else {
      setSearchJobs([]);
    }
  }

  return (
    <div>
      <div class="search-container">
        <div class="search-box">
            <input type='text' placeholder='Search..' value={searchTerm} onChange={handleChange} />
        </div>
      </div>
      <div class="content">
        <ul class="search-results">
              {
                jobs.map((job)=> (
                  <li>
                    <h3  key={job.id} class="title">{job.title}</h3>
                    <p class="description">A short description of the first search result.</p>
                  </li>
                  ))
              }
        </ul>
      </div>
    </div>
  );
}

export default App;
