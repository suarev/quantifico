import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

const ParallelCoordinates = ({ playerName = "Bruno Fernandes" }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [availableMetrics, setAvailableMetrics] = useState([]);
  const [metrics, setMetrics] = useState([
    { label: 'Position', value: 'pos_' },
    { label: 'Minutes', value: 'minutes_played' },
    { label: 'Age', value: 'age_' },
    { label: 'Value', value: 'value' },
    { label: 'Goals', value: 'goals' },
    { label: 'Assists', value: 'assists' },
    { label: 'SCA', value: 'sca' },
    { label: 'Key Passes', value: 'key_passes' },
    { label: 'Tackles + Int', value: 'tackles_interceptions' },
    { label: 'Prog Carries', value: 'progressive_carries' },
    { label: 'Prog Passes', value: 'progressive_passes' }
  ]);

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
        
        const response = await axios.get(`http://127.0.0.1:8001/api/parallel/${playerName}`, {
          params: { metrics: JSON.stringify(metricsMap) }
        });
        setData(response.data);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchData();
  }, [playerName, metrics]);

  useEffect(() => {
    if (!data) return;

    d3.select(svgRef.current).selectAll('*').remove();
    d3.selectAll('.parallel-tooltip').remove();

    const margin = { top: 50, right: 100, bottom: 30, left: 100 };
    const width = 1200 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'parallel-tooltip fixed hidden bg-black/90 text-white p-2 rounded text-xs z-[1000]')
      .style('pointer-events', 'none');

    const metricNames = metrics.map(m => m.label);
    const xScale = d3.scalePoint()
      .domain(metricNames)
      .range([0, width]);

    const yScales = {};
    metricNames.forEach(metric => {
      if (metric === 'Position') {
        yScales[metric] = d3.scalePoint()
          .domain(data.domains.Position)
          .range([height, 0])
          .padding(0.5);
      } else {
        const values = data.data.map(d => d.values[metric]);
        yScales[metric] = d3.scaleLinear()
          .domain([d3.min(values), d3.max(values)])
          .range([height, 0])
          .nice();
      }
    });


    metricNames.forEach((metric, i) => {
      const g = svg.append('g')
        .attr('transform', `translate(${xScale(metric)},0)`);

      const axis = d3.axisLeft(yScales[metric]);
      g.call(axis)
        .call(g => g.selectAll('text').attr('fill', '#888'));


      const container = g.append('foreignObject')
        .attr('x', -60)
        .attr('y', -40)
        .attr('width', 120)
        .attr('height', 20);

      const select = container.append('xhtml:select')
        .attr('class', 'bg-transparent text-gray-400 hover:text-white text-xs cursor-pointer border-none focus:outline-none focus:ring-0 appearance-none w-full text-center')
        .style('background-color', 'transparent')
        .on('change', function(event) {
          const newMetricValue = event.target.value;
          const newMetricLabel = event.target.options[event.target.selectedIndex].text;
          
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
            .text(availableMetric.label)  
            .style('background-color', '#1a1f17');
      });


      g.selectAll('text')
        .attr('transform', 'rotate(-20)')
        .style('text-anchor', 'end');
    });

    const line = d3.line()
      .x(d => xScale(d.metric))
      .y(d => yScales[d.metric](d.value));

    data.data.forEach(player => {
      const playerData = metricNames.map(metric => ({
        metric: metric,
        value: player.values[metric]
      }));

      const isMainPlayer = player.player === playerName;

      const path = svg.append('path')
        .datum(playerData)
        .attr('fill', 'none')
        .attr('stroke', isMainPlayer ? '#4CAF50' : '#ffffff')
        .attr('stroke-width', isMainPlayer ? 2 : 1)
        .attr('opacity', isMainPlayer ? 1 : 0.2)
        .attr('d', line)
        .style('cursor', 'pointer');

      path
        .on('mouseover', function(event) {
          d3.select(this)
            .attr('stroke-width', isMainPlayer ? 3 : 2)
            .attr('opacity', 1);

          tooltip.html(`
            <div class="font-bold text-base ${isMainPlayer ? 'text-green-400' : ''} mb-2">${player.player}</div>
            ${metricNames.map(metric => `
              <div class="grid grid-cols-2 gap-2">
                <span class="text-gray-400">${metric}:</span>
                <span class="text-right">${
                  metric === 'Position' 
                    ? player.values[metric]
                    : typeof player.values[metric] === 'number' 
                      ? player.values[metric].toFixed(1)
                      : player.values[metric]
                }</span>
              </div>
            `).join('')}
          `)
            .style('left', `${event.pageX}px`)
            .style('top', `${event.pageY - 10}px`)
            .classed('hidden', false);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('left', `${event.pageX}px`)
            .style('top', `${event.pageY - 10}px`);
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('stroke-width', isMainPlayer ? 2 : 1)
            .attr('opacity', isMainPlayer ? 1 : 0.2);
          tooltip.classed('hidden', true);
        });

      if (isMainPlayer) {
        svg.selectAll('.player-point')
          .data(playerData)
          .enter()
          .append('circle')
          .attr('cx', d => xScale(d.metric))
          .attr('cy', d => yScales[d.metric](d.value))
          .attr('r', 4)
          .attr('fill', '#4CAF50');
      }
    });

  }, [data, availableMetrics, metrics]);

  if (error) return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5">
      <div className="text-red-500">Error loading parallel coordinates: {error}</div>
    </div>
  );

  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 h-full">
      <h3 className="text-gray-400 text-sm mb-4">Team Ranking Analysis - Parallel Coordinates Plot</h3>
      <div ref={containerRef} className="relative w-full overflow-x-auto">
        <div className="min-w-[1200px] h-[400px]">
          <svg ref={svgRef} className="w-full h-full" />
        </div>
      </div>
    </div>
  );
};

export default ParallelCoordinates;