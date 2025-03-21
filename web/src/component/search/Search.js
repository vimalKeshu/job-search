import './Search.css';
import React, {useState, useEffect} from 'react';
import Loader from '../loader/Loader';
import { JobSearchAPI } from '../../api/JobSearchAPI';

function Search() {
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(false);
    const [jobs, setSearchJobs] = useState([
      // {'id':1,'title': 'Software Engineer, Machine Learning', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':2,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':3,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':4,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':5,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':6,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':7,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':8,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':9,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':10,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':1,'title': 'Software Engineer, Machine Learning', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':2,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':3,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':4,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':5,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':6,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':7,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':8,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':9,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'},
      // {'id':10,'title': 'Software Engineer', 'company': 'Google', 'url': 'http://localhost:8080'}    
    ]);
  
    const fetchJobs = async (query) => {
      setLoading(true);
      JobSearchAPI.search(query)
        .then((jobs) => setSearchJobs(jobs))
        .catch((error) => console.error(error))
        .finally(() => setLoading(false))
    }
        
    useEffect(() => {
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
      <div class="container">
        <div>
          {loading ? <Loader /> : <div></div>}
        </div>  
        <div class="search-container">
          <div class="search-box">
              <textarea placeholder='Search..' value={searchTerm}  onChange={handleChange}  onKeyPress={handleKeyPress} />
              <button type="button" onClick={handleSearch}>
                <i>Search</i>
              </button>
          </div>
        </div>
        <div class="search-results">
          <ul>
                {
                  jobs.map((job)=> (
                    <li key={job.id}>
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
  
  export default Search;
  