import React from 'react';

const Footer = () => {
  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 mt-5">
      <h3 className="text-gray-400 text-sm mb-4">Content Attribution</h3>
      <div className="text-xs">
        <ul className="text-gray-500 space-y-1">
          <li>• Player statistics sourced from FBref.com and StatsBomb</li>
          <li>• Match and positional data provided by Sofascore</li>
          <li>• Player images sourced via Google Custom Search API</li>
          <li>• This application is created for educational purposes only as part of academic research</li>
        </ul>
        <p className="text-gray-400 mt-3">
          © {new Date().getFullYear()} Quantifico - Created by Saurav Sharma for academic purposes
        </p>
      </div>
    </div>
  );
};

export default Footer;