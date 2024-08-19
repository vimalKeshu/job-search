import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
    return (
        <footer>
            <p>© 2024 JOB SEARCH</p>
            <p><Link to="/about">About</Link></p>
        </footer>
    );
}


export default Footer;