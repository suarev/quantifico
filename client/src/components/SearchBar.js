import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const SearchBar = ({ onPlayerSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!searchTerm.trim()) {
        setSuggestions([]);
        return;
      }

      setIsLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/search?q=${searchTerm}`);
        setSuggestions(response.data.players.slice(0, 5));
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      }
      setIsLoading(false);
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
    setShowDropdown(true);
  };

  const handlePlayerClick = (player) => {
    setSearchTerm(player);
    setShowDropdown(false);
    onPlayerSelect(player);
  };

  return (
    <div className="relative w-96" ref={dropdownRef}>
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setShowDropdown(true)}
          placeholder="Search for a player..."
          className="w-full px-4 py-2 bg-[#1a1f17] text-white rounded-lg border border-[#2f3c28] focus:outline-none focus:border-[#4CAF50]"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-[#4CAF50]"></div>
          </div>
        )}
      </div>

      {showDropdown && suggestions.length > 0 && (
        <div className="absolute w-full mt-2 bg-[#1a1f17] border border-[#2f3c28] rounded-lg shadow-lg z-50">
          {suggestions.map((player, index) => (
            <div
              key={index}
              className="px-4 py-2 hover:bg-[#2f3c28] cursor-pointer text-white"
              onClick={() => handlePlayerClick(player)}
            >
              {player}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;