import React, { useState, useEffect } from "react";
import axios from "axios";
import fetchPlayerImage from "../utils/fetchPlayerImage"; 

const PlayerProfile = ({ playerName }) => {
  const [playerData, setPlayerData] = useState(null);
  const [playerImage, setPlayerImage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.get(
          `http://127.0.0.1:8001/api/player/${playerName}`
        );
        setPlayerData(response.data);

        const image = await fetchPlayerImage(playerName);
        setPlayerImage(image);
      } catch (err) {
        setError(err.message);
      }

      setIsLoading(false);
    };

    fetchData();
  }, [playerName]);

  if (isLoading) {
    return <div>Loading player data...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 h-full flex flex-col items-center">
      <h2 className="text-2xl font-bold text-white mb-6">{playerData.name}</h2>
      
      <div className="image-container">
  {playerImage ? (
    <img src={playerImage} alt={playerName} className="player-image" />
  ) : (
    <span className="text-white">No Image Found</span>
  )}
</div>


      {/* Badges row */}
      <div className="flex gap-3 mb-6">
        <div className="bg-[#1A1F17] px-3 py-1 rounded flex items-center gap-2">
          <span className="text-gray-300">{playerData.nationality}</span>
        </div>
        <div className="bg-[#1A1F17] px-3 py-1 rounded flex items-center gap-2">
          <span className="text-gray-300">{playerData.team}</span>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-6 w-full text-center">
        <div className="flex flex-col items-center">
          <div className="text-gray-400 text-sm">Position</div>
          <div className="font-bold text-white">{playerData.position}</div>
        </div>
        <div className="flex flex-col items-center">
          <div className="text-gray-400 text-sm">Age</div>
          <div className="font-bold text-white">{playerData.age}</div>
        </div>
        <div className="flex flex-col items-center">
          <div className="text-gray-400 text-sm">Value</div>
          <div className="font-bold text-white">{playerData.value}</div>
        </div>
        <div className="flex flex-col items-center">
          <div className="text-gray-400 text-sm">Matches</div>
          <div className="font-bold text-white">{playerData.matches_played}</div>
        </div>
      </div>
    </div>
  );
};

export default PlayerProfile;
