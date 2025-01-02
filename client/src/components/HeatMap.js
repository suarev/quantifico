import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

const HeatMap = ({ playerName = "Bruno Fernandes" }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const HEATMAP_CONFIG = {
    width: 500,  
    height: 350, 
    margin: {   
      top: 10,
      right: 10,
      bottom: 10,
      left: 10
    },

    bandwidth: 15,
    thresholds: 70,
    opacity: 0.08,
    background: '#0B3B0B',
    pitch_line_color: '#FFFFFF',
    pitch_line_width: 2,
    pitch_line_opacity: 0.8,
    cellSize: 2,
    weight: 1,
    color_start: '#c5e617',
    color_end: '#ff0000'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8001/api/heatmap/${playerName}`);
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

    const width = HEATMAP_CONFIG.width - HEATMAP_CONFIG.margin.left - HEATMAP_CONFIG.margin.right;
    const height = HEATMAP_CONFIG.height - HEATMAP_CONFIG.margin.top - HEATMAP_CONFIG.margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', HEATMAP_CONFIG.width)
      .attr('height', HEATMAP_CONFIG.height)
      .append('g')
      .attr('transform', `translate(${HEATMAP_CONFIG.margin.left},${HEATMAP_CONFIG.margin.top})`);

    const clipPath = svg.append('defs')
      .append('clipPath')
      .attr('id', 'pitch-clip');

    clipPath.append('rect')
      .attr('width', width)
      .attr('height', height);


    const xScale = d3.scaleLinear()
      .domain([0, data.pitch_dimensions.width])
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, data.pitch_dimensions.height])
      .range([height, 0]);

    const drawPitch = () => {
      svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', HEATMAP_CONFIG.background)
        .attr('stroke', HEATMAP_CONFIG.pitch_line_color)
        .attr('stroke-width', HEATMAP_CONFIG.pitch_line_width)
        .attr('stroke-opacity', HEATMAP_CONFIG.pitch_line_opacity);

      const pitch = svg.append('g')
        .attr('class', 'pitch-lines')
        .style('stroke', HEATMAP_CONFIG.pitch_line_color)
        .style('stroke-width', HEATMAP_CONFIG.pitch_line_width)
        .style('stroke-opacity', HEATMAP_CONFIG.pitch_line_opacity);

 
      pitch.append('line')
        .attr('x1', width/2)
        .attr('y1', 0)
        .attr('x2', width/2)
        .attr('y2', height);

      pitch.append('circle')
        .attr('cx', width/2)
        .attr('cy', height/2)
        .attr('r', xScale(9.15))
        .attr('fill', 'none');

      pitch.append('circle')
        .attr('cx', width/2)
        .attr('cy', height/2)
        .attr('r', 2)
        .attr('fill', HEATMAP_CONFIG.pitch_line_color);

      pitch.append('line')
        .attr('x1', xScale(16.5))
        .attr('y1', yScale(65))
        .attr('x2', xScale(16.5))
        .attr('y2', yScale(25));
      pitch.append('line')
        .attr('x1', 0)
        .attr('y1', yScale(65))
        .attr('x2', xScale(16.5))
        .attr('y2', yScale(65));
      pitch.append('line')
        .attr('x1', xScale(16.5))
        .attr('y1', yScale(25))
        .attr('x2', 0)
        .attr('y2', yScale(25));

      pitch.append('line')
        .attr('x1', width)
        .attr('y1', yScale(65))
        .attr('x2', width - xScale(16.5))
        .attr('y2', yScale(65));
      pitch.append('line')
        .attr('x1', width - xScale(16.5))
        .attr('y1', yScale(65))
        .attr('x2', width - xScale(16.5))
        .attr('y2', yScale(25));
      pitch.append('line')
        .attr('x1', width - xScale(16.5))
        .attr('y1', yScale(25))
        .attr('x2', width)
        .attr('y2', yScale(25));

      pitch.append('line')
        .attr('x1', 0)
        .attr('y1', yScale(54))
        .attr('x2', xScale(5.5))
        .attr('y2', yScale(54));
      pitch.append('line')
        .attr('x1', xScale(5.5))
        .attr('y1', yScale(54))
        .attr('x2', xScale(5.5))
        .attr('y2', yScale(36));
      pitch.append('line')
        .attr('x1', xScale(5.5))
        .attr('y1', yScale(36))
        .attr('x2', 0)
        .attr('y2', yScale(36));

      pitch.append('line')
        .attr('x1', width)
        .attr('y1', yScale(54))
        .attr('x2', width - xScale(5.5))
        .attr('y2', yScale(54));
      pitch.append('line')
        .attr('x1', width - xScale(5.5))
        .attr('y1', yScale(54))
        .attr('x2', width - xScale(5.5))
        .attr('y2', yScale(36));
      pitch.append('line')
        .attr('x1', width - xScale(5.5))
        .attr('y1', yScale(36))
        .attr('x2', width)
        .attr('y2', yScale(36));

      pitch.append('circle')
        .attr('cx', xScale(11))
        .attr('cy', height/2)
        .attr('r', 2)
        .attr('fill', HEATMAP_CONFIG.pitch_line_color);
      pitch.append('circle')
        .attr('cx', width - xScale(11))
        .attr('cy', height/2)
        .attr('r', 2)
        .attr('fill', HEATMAP_CONFIG.pitch_line_color);
    };


    drawPitch();


    const contours = d3.contourDensity()
      .x(d => xScale(d.x))
      .y(d => yScale(d.y))
      .size([width, height])
      .bandwidth(HEATMAP_CONFIG.bandwidth)
      .thresholds(HEATMAP_CONFIG.thresholds)
      .cellSize(HEATMAP_CONFIG.cellSize)
      .weight(HEATMAP_CONFIG.weight)
      (data.coordinates);

    const colorScale = d3.scaleSequential()
      .domain([0, d3.max(contours, d => d.value)])
      .interpolator(t => d3.interpolateRgb(HEATMAP_CONFIG.color_start, HEATMAP_CONFIG.color_end)(t));

    const heatmapGroup = svg.append('g')
      .attr('clip-path', 'url(#pitch-clip)');

    heatmapGroup.selectAll('path')
      .data(contours)
      .enter()
      .append('path')
      .attr('d', d3.geoPath())
      .attr('fill', d => colorScale(d.value))
      .attr('opacity', HEATMAP_CONFIG.opacity);

  }, [data]);

  if (error) return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5">
      <div className="text-red-500">Error loading heatmap: {error}</div>
    </div>
  );

  return (
    <div className="bg-[#11150F]/95 rounded-2xl p-5 h-full">
      <h3 className="text-gray-400 text-sm mb-4">Position Heat Map (Season Average)</h3>
      <div ref={containerRef} className="relative flex items-center justify-center">
        <svg ref={svgRef} className="w-full h-full" preserveAspectRatio="xMidYMid meet" />
      </div>
    </div>
  );
};

export default HeatMap;