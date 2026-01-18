import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

// Color palette for different categories
const COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#a4de6c',
  '#d0ed57', '#83a6ed', '#8dd1e1', '#82ca9d', '#a4de6c'
];

function BrowsingChart({ chartData }) {
  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return null;
  }

  const { title, data, xAxis, yAxis, yAxisLabel } = chartData;

  return (
    <div style={{ width: '100%', marginTop: '20px', marginBottom: '30px' }}>
      <h3 style={{ textAlign: 'center', marginBottom: '15px', color: '#333' }}>{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={xAxis}
            angle={-45}
            textAnchor="end"
            height={100}
            interval={0}
            style={{ fontSize: '12px' }}
          />
          <YAxis
            label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            formatter={(value, name) => {
              if (name === 'minutes') {
                const hours = Math.floor(value / 60);
                const mins = Math.round(value % 60);
                if (hours > 0) {
                  return [`${hours}h ${mins}m`, 'Time Spent'];
                }
                return [`${mins}m`, 'Time Spent'];
              }
              return [value, name];
            }}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          <Bar dataKey={yAxis} name="Time Spent (minutes)" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BrowsingChart;
