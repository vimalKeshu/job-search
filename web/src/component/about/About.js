import React from 'react';
import './About.css';

const About = () => {
  return (
    // <div className="about-container">
    //   <h1>About Us</h1>
    //   <p>
    //     Welcome to our website! We are a team of passionate individuals dedicated to providing you with the best service. Our mission is to...
    //   </p>
    //   <p>
    //     Our team includes experts in various fields, all working together to achieve our goals and ensure that you have a fantastic experience with us.
    //   </p>
    //   <p>
    //     Thank you for visiting our website. If you have any questions, feel free to reach out to us!
    //   </p>
    // </div>
      <section class="about">
          <div class="about-content">
              <img src="vimal_chaudhari.jpeg" alt="Vimal Chaudhari" class="profile-photo" />
              <div class="description">
                  {/* <h1>About Me</h1> */}
                  <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vel lacus eget magna pharetra tincidunt. Praesent et urna ut urna vulputate cursus non at sapien. Donec sit amet felis nec velit blandit facilisis.</p>
                  <p>Suspendisse potenti. Quisque viverra felis nec sollicitudin tempus. Duis eget bibendum nulla. Integer auctor ex nec libero elementum, nec rhoncus nulla tristique.</p>
              </div>
          </div>
      </section>    
  );
};

export default About;