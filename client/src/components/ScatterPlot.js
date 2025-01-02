import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

const ScatterPlot = ({ playerName = "Bruno Fernandes" }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8001/api/scatter/${playerName}`);
        setData(response.data);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchData();
  }, [playerName]);

  useEffect(() => {
    if (!data) return;

    d3.select(svgRef.current).selectAll('*').remove();
    d3.selectAll('.scatter-tooltip').remove();

    const margin = { top: 30, right: 50, bottom: 50, left: 50 };
    const width = 400 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);


    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'scatter-tooltip fixed hidden bg-black/90 text-white p-2 rounded text-xs z-[1000]')
      .style('pointer-events', 'none');


    const xScale = d3.scaleLinear()
      .domain(d3.extent(data.data, d => d.attacking))
      .nice()
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data.data, d => d.defensive))
      .nice()
      .range([height, 0]);


    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .call(g => g.selectAll('text').attr('fill', '#888'));

    svg.append('g')
      .call(d3.axisLeft(yScale))
      .call(g => g.selectAll('text').attr('fill', '#888'));


    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .attr('fill', '#888')
      .attr('text-anchor', 'middle')
      .text(`Attacking Component (${data.variance_explained.attacking}% var.)`);

    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -40)
      .attr('fill', '#888')
      .attr('text-anchor', 'middle')
      .text(`Defensive Component (${data.variance_explained.defensive}% var.)`);


    svg.selectAll('.point')
      .data(data.data)
      .enter()
      .append('circle')
      .attr('cx', d => xScale(d.attacking))
      .attr('cy', d => yScale(d.defensive))
      .attr('r', d => d.player === playerName ? 6 : 4)
      .attr('fill', d => d.player === playerName ? '#4CAF50' : '#ffffff')
      .attr('opacity', d => d.player === playerName ? 1 : 0.5)
      .attr('stroke', d => d.player === playerName ? '#4CAF50' : 'none')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('r', d.player === playerName ? 8 : 6)
          .attr('opacity', 1);

        tooltip.html(`
          <div class="font-bold text-base ${d.player === playerName ? 'text-green-400' : ''} mb-2">${d.player}</div>
          <div class="text-gray-400">${d.team}</div>
          <div class="grid grid-cols-2 gap-x-3 gap-y-1 mt-1">
            <span class="text-gray-400">Attacking:</span>
            <span class="text-right">${d.attacking.toFixed(2)}</span>
            <span class="text-gray-400">Defensive:</span>
            <span class="text-right">${d.defensive.toFixed(2)}</span>
          </div>
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
      .on('mouseout', function(d) {
        d3.select(this)
          .attr('r', d => d.player === playerName ? 6 : 4)
          .attr('opacity', d => d.player === playerName ? 1 : 0.5);
        tooltip.classed('hidden', true);
      });

  }, [data]);

  if (error) return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5">
      <div className="text-red-500">Error loading scatter plot: {error}</div>
    </div>
  );

  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 h-full">
      <h3 className="text-gray-400 text-sm mb-4">Performance Distribution - Biplot Analysis</h3>
      <div ref={containerRef} className="relative flex items-center justify-center">
        <svg ref={svgRef} />
      </div>
    </div>
  );
};

export default ScatterPlot;