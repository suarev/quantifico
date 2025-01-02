import React, { useState } from 'react';
import PlayerProfile from './components/PlayerProfile';
import RadarChart from './components/RadarChart';
import HeatMap from './components/HeatMap';
import ParallelCoordinates from './components/ParallelCoordinates';
import SearchBar from './components/SearchBar';
import ScatterPlot from './components/ScatterPlot';
import Footer from './components/Footer';

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState("Bruno Fernandes");
  return (
    <div className="min-h-screen bg-[#0B0E0A] overflow-y-auto">
      <nav className="fixed top-0 left-0 w-full h-16 bg-[#11150F]/95 z-[1000] px-6 flex items-center justify-between border-b border-[#2f3c28]">
        <div className="text-2xl font-bold text-white">Quantifico</div>
        <SearchBar onPlayerSelect={setSelectedPlayer} />
      </nav>

      <div className="fixed top-16 left-0 w-full h-1/2 z-20 bg-[radial-gradient(ellipse_100%_100%_at_50%_-50%,rgba(240,239,184,0.3)_0%,rgba(255,255,255,0)_100%)]" />
        
      <div className="fixed top-16 left-0 w-full h-screen flex z-10">
        {[...Array(12)].map((_, i) => (
          <div 
            key={i} 
            className={`flex-1 ${i % 2 === 0 ? 'bg-[#11150F]' : 'bg-[#141A12]'}`} 
          />
        ))}
      </div>
      <img 
        src="/images/soccer-lines.png" 
        alt="pitch lines" 
        className="fixed top-[calc(16px-2vw)] left-[10vw] w-[87vw] z-30"
      />
      <div className="relative z-40 p-10 pt-16">
        <div className="grid grid-cols-3 auto-rows-min gap-5">
          <PlayerProfile playerName={selectedPlayer} />
          <RadarChart playerName={selectedPlayer} />
          <div className="space-y-5">
            <HeatMap playerName={selectedPlayer} />
            <div className="bg-[#11150F]/95 rounded-2xl p-5">
              <h3 className="text-gray-400 text-sm mb-4">Performance Distribution</h3>
            </div>
          </div>
          
          <div className="col-span-2">
            <ParallelCoordinates playerName={selectedPlayer} />
          </div>
          <div className="col-start-3">
            <ScatterPlot playerName={selectedPlayer} />
          </div>
        </div>
        <Footer />
      </div>
    </div>
  );
}

export default App;