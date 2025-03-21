import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
    return (
        <header>
            <h1>
                <span>
                    <Link to="/">
                        <img src="job_search_logo.svg" alt="Job Search" />OB SEARCH
                    </Link>
                </span>
            </h1>
        </header>
    );
}


export default Header;