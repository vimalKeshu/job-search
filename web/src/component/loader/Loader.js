import React from 'react';
import './Loader.css'; // Import the CSS file for styling

const Loader = () => (
    <div className="loader">
    <div className="image-slider">
      <img src="/assets/image1.svg" alt="1" class="slide image1" />
      <img src="/assets/image2.svg" alt="2" class="slide image2" />
    </div>
  </div>
);

export default Loader;
