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
    //fetchJobs('');
  }, []);

  const handleChange = (event) => {
    setSearchTerm(event.target.value);
  }

  // Function to trigger search on submit
  const handleSearch = (event) => {
    event.preventDefault();
    if (searchTerm.length >= 3) {
      fetchJobs(searchTerm);
    } else {
      setSearchJobs([]);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (searchTerm.length >= 3) {
        fetchJobs(searchTerm);
      } else {
        setSearchJobs([]);
      }
    }
  };

  return (
    <div>
      <div class="search-container">
        <div class="search-box">
            <input type='text' placeholder='Search..' value={searchTerm}  onChange={handleChange}  onKeyPress={handleKeyPress} />
            <button type="button" onClick={handleSearch} class="search-button">
              <i className="fas fa-search"></i>
            </button>
        </div>
      </div>
      <div class="content">
        <ul class="search-results">
              {
                jobs.map((job)=> (
                  <li>
                    <span class="title">{job.title}</span>
                    <span class="company">{job.company}</span>
                    <a href={job.url} class="link">Description</a>
                  </li>
                  ))
              }
        </ul>
      </div>
    </div>
  );
}

export default App;
