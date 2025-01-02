import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

const RadarChart = ({ playerName = "Bruno Fernandes" }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [availableMetrics, setAvailableMetrics] = useState([]);
  const [metrics, setMetrics] = useState([
    { label: 'Shot Creating Actions', value: 'sca' },
    { label: 'Key Passes', value: 'key_passes' },
    { label: 'Prog. Carries', value: 'progressive_carries' },
    { label: 'Prog. Passes', value: 'progressive_passes' },
    { label: 'xAG', value: 'xag' },
    { label: 'npxG', value: 'npxg' },
    { label: 'Tackles+Interceptions', value: 'tackles_interceptions' },
    { label: 'Take-ons Succ.', value: 'dribbles_completed_pct' },
    { label: 'Recoveries', value: 'passes_received' }
]);


  const CHART_CONFIG = {
    width: 440,
    height: 440,
    xOffset: -20,
    yOffset: 0,
    labelSpacing: 30,
    legendX: -160,
    legendY: -200,
    margin: 90,
    pointRadius: 4
  };


  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8001/api/available-metrics');
        setAvailableMetrics(response.data.metrics);
      } catch (err) {
        console.error('Error fetching metrics:', err);
      }
    };
    fetchMetrics();
  }, []);


  useEffect(() => {
    const fetchData = async () => {
      try {
        const metricsMap = Object.fromEntries(
          metrics.map(m => [m.label, m.value])
        );
        
        const response = await axios.get(`http://127.0.0.1:8001/api/radar/${playerName}`, {
          params: { metrics: JSON.stringify(metricsMap) }
        });
        setData(response.data);
      } catch (err) {
        setError(err.message);
      }
    };

    if (metrics.length > 0) {
      fetchData();
    }
  }, [playerName, metrics]);

  useEffect(() => {
    if (!data) return;

    d3.select(svgRef.current).selectAll('*').remove();
    d3.selectAll('.radar-tooltip').remove();

    const radius = Math.min(CHART_CONFIG.width, CHART_CONFIG.height) / 2 - CHART_CONFIG.margin;
    const svg = d3.select(svgRef.current)
      .attr('width', CHART_CONFIG.width)
      .attr('height', CHART_CONFIG.height)
      .append('g')
      .attr('transform', `translate(${CHART_CONFIG.width/2 + CHART_CONFIG.xOffset},${CHART_CONFIG.height/2 + CHART_CONFIG.yOffset})`);

    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'radar-tooltip fixed hidden bg-black/90 text-white p-2 rounded text-xs z-[1000]')
      .style('pointer-events', 'none');

    const metricNames = metrics.map(m => m.label);
    const angleScale = d3.scaleLinear()
      .domain([0, metrics.length])
      .range([0, 2 * Math.PI]);

    const radiusScale = d3.scaleLinear()
      .domain([0, 100])
      .range([0, radius]);

    const levels = 5;
    for (let i = 0; i < levels; i++) {
      svg.append('circle')
        .attr('cx', 0)
        .attr('cy', 0)
        .attr('r', radius * (i + 1) / levels)
        .attr('fill', 'none')
        .attr('stroke', '#2f3c28')
        .attr('stroke-width', 1)
        .attr('opacity', 0.3);

      svg.append('text')
        .attr('x', 5)
        .attr('y', -radius * (i + 1) / levels)
        .attr('dy', '0.3em')
        .attr('fill', '#666')
        .attr('font-size', '10px')
        .text(`${(i + 1) * 20}%`);
    }

    const axes = svg.selectAll('.axis')
      .data(metricNames)
      .enter()
      .append('g')
      .attr('class', 'axis');

    axes.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => radius * Math.cos(angleScale(i) - Math.PI/2))
      .attr('y2', (d, i) => radius * Math.sin(angleScale(i) - Math.PI/2))
      .attr('stroke', '#2f3c28')
      .attr('stroke-width', 1);

    const playerPoints = metricNames.map((metric, i) => ({
      x: radiusScale(data.player[metric]) * Math.cos(angleScale(i) - Math.PI/2),
      y: radiusScale(data.player[metric]) * Math.sin(angleScale(i) - Math.PI/2)
    }));

    const leaguePoints = metricNames.map((metric, i) => ({
      x: radiusScale(data.league_average[metric]) * Math.cos(angleScale(i) - Math.PI/2),
      y: radiusScale(data.league_average[metric]) * Math.sin(angleScale(i) - Math.PI/2)
    }));

    svg.selectAll('.player-line')
      .data(playerPoints)
      .enter()
      .append('line')
      .attr('x1', (d, i) => playerPoints[i].x)
      .attr('y1', (d, i) => playerPoints[i].y)
      .attr('x2', (d, i) => playerPoints[(i + 1) % playerPoints.length].x)
      .attr('y2', (d, i) => playerPoints[(i + 1) % playerPoints.length].y)
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2);

    svg.selectAll('.player-point')
      .data(playerPoints)
      .enter()
      .append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', CHART_CONFIG.pointRadius)
      .attr('fill', '#4CAF50');

    svg.selectAll('.league-line')
      .data(leaguePoints)
      .enter()
      .append('line')
      .attr('x1', (d, i) => leaguePoints[i].x)
      .attr('y1', (d, i) => leaguePoints[i].y)
      .attr('x2', (d, i) => leaguePoints[(i + 1) % leaguePoints.length].x)
      .attr('y2', (d, i) => leaguePoints[(i + 1) % leaguePoints.length].y)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5);

    svg.selectAll('.league-point')
      .data(leaguePoints)
      .enter()
      .append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', CHART_CONFIG.pointRadius - 1)
      .attr('fill', '#ffffff')
      .attr('opacity', 0.5);

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${CHART_CONFIG.legendX}, ${CHART_CONFIG.legendY})`);

    legend.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', 20)
      .attr('y2', 0)
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2);

    legend.append('circle')
      .attr('cx', 10)
      .attr('cy', 0)
      .attr('r', CHART_CONFIG.pointRadius)
      .attr('fill', '#4CAF50');

    legend.append('text')
      .attr('x', 30)
      .attr('y', 0)
      .attr('dy', '0.32em')
      .attr('fill', '#888')
      .attr('font-size', '11px')
      .text('Player');

    legend.append('line')
      .attr('x1', 0)
      .attr('y1', 20)
      .attr('x2', 20)
      .attr('y2', 20)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5);

    legend.append('circle')
      .attr('cx', 10)
      .attr('cy', 20)
      .attr('r', CHART_CONFIG.pointRadius - 1)
      .attr('fill', '#ffffff')
      .attr('opacity', 0.5);

    legend.append('text')
      .attr('x', 30)
      .attr('y', 20)
      .attr('dy', '0.32em')
      .attr('fill', '#888')
      .attr('font-size', '11px')
      .text('League Average');


    const labelRadius = radius + CHART_CONFIG.labelSpacing;
    axes.each(function(metric, i) {
      const angle = angleScale(i) - Math.PI/2;
      const x = labelRadius * Math.cos(angle);
      const y = labelRadius * Math.sin(angle);
      
      const container = d3.select(this)
        .append('foreignObject')
        .attr('x', x - 60)
        .attr('y', y - 10)
        .attr('width', 120)
        .attr('height', 20);

      const select = container.append('xhtml:select')
        .attr('class', 'bg-transparent text-gray-400 hover:text-white text-xs cursor-pointer border-none focus:outline-none focus:ring-0 appearance-none w-full text-center')
        .style('background-color', 'transparent')
        .on('change', function(event) {
          const newMetricValue = event.target.value;
          const newMetricLabel = event.target.value; 
          
          setMetrics(currentMetrics => {
            const newMetrics = [...currentMetrics];
            newMetrics[i] = { label: newMetricLabel, value: newMetricValue };
            return newMetrics;
          });
        });

      availableMetrics.forEach(availableMetric => {
        select.append('option')
          .attr('value', availableMetric.value)
          .property('selected', metrics[i].value === availableMetric.value)
          .text(availableMetric.value)
          .style('background-color', '#1a1f17');
      });

      container
        .on('mouseover', function(event) {
          if (!data.raw_values[metric]) return;
          
          tooltip.html(`
            <div class="font-bold mb-1">${metric}</div>
            <div class="grid grid-cols-2 gap-x-3 gap-y-1">
              <div class="text-green-400">Player:</div>
              <div class="text-right">${data.raw_values[metric].player.toFixed(1)}</div>
              <div class="text-gray-400">League Avg:</div>
              <div class="text-right">${data.raw_values[metric].league_avg.toFixed(1)}</div>
              <div class="text-gray-400">League Max:</div>
              <div class="text-right">${data.raw_values[metric].max.toFixed(1)}</div>
            </div>
          `)
          .style('left', `${event.pageX}px`)
          .style('top', `${event.pageY - 10}px`)
          .classed('hidden', false);
        })
        .on('mousemove', function(event) {
          tooltip
            .style('left', `${event.pageX}px`)
            .style('top', `${event.pageY - 10}px`);
        })
        .on('mouseout', function() {
          tooltip.classed('hidden', true);
        });
    });

  }, [data, availableMetrics, metrics]);

  if (error) return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5">
      <div className="text-red-500">Error loading radar chart: {error}</div>
    </div>
  );

  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 h-full">
      <h3 className="text-gray-400 text-sm mb-4">Performance Metrics - Radar Chart</h3>
      <div ref={containerRef} className="relative flex items-center justify-center">
        <svg ref={svgRef} />
      </div>
    </div>
  );
};

export default RadarChart;