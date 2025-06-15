import React from 'react';
import { motion } from 'framer-motion';

// Team member data with profile images
const teamMembers = [
  { id: 1, name: 'Priyanka Sundalam', image: './img/bbg1.jpg' },
  { id: 2, name: 'Aditi Deshpande', image: './img/bbg2.jpg' },
  { id: 3, name: 'Ankita Advitot', image: './img/bbg3.jpg' },
  { id: 4, name: 'Tejas Jahagirdar', image: './img/bbg4.jpg' },
];

const Footer = () => {
  // Animation variants for image
  const imageVariants = {
    initial: { scale: 1 },
    hover: { scale: 1.5, transition: { duration: 0.3 } },
  };

  // Animation variants for name
  const nameVariants = {
    initial: { opacity: 0, y: 10 },
    hover: { opacity: 1, y: 20, transition: { duration: 0.3 } },
  };

  return (
    <footer className="bg-gray-900 text-white py-8 w-full border-t border-gray-700">
      <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
        {/* Left Side: Logo and Tagline */}
        <div className="mb-6 md:mb-0 text-center md:text-left">
          <h2 className="text-3xl font-extrabold text-white">TripCraft</h2>
          <p className="text-sm text-gray-400 mt-2">
            Explore the universe, one journey at a time.
          </p>
        </div>

        {/* Right Side: Team Member Images */}
        <div className="flex flex-col md:flex-row gap-6 items-center">
          {teamMembers.map((member) => (
            <motion.div
              key={member.id}
              className="relative flex flex-col items-center"
              initial="initial"
              whileHover="hover"
            >
              <motion.img
                src={member.image}
                alt={member.name}
                className="w-14 h-14 rounded-full object-cover border-2 border-blue-600"
                variants={imageVariants}
              />
              <motion.span
                className="absolute bottom-[-2rem] text-xs text-white font-medium whitespace-nowrap"
                variants={nameVariants}
              >
                {member.name}
              </motion.span>
            </motion.div>
          ))}
        </div>
      </div>
      <div className="mt-8 text-center text-gray-500 text-xs">
        © {new Date().getFullYear()} TripCraft. All Rights Reserved.
      </div>
    </footer>
  );
};

export default Footer;