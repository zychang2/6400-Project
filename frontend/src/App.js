import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';
import datajson from './cities.json';
import axios from 'axios';

const App = () => {
  const [searchQuery1, setSearchQuery1] = useState('');
  const [searchQuery2, setSearchQuery2] = useState('');
  const [filteredData1, setFilteredData1] = useState([]);
  const [filteredData2, setFilteredData2] = useState([]);
  const [selectedResult1, setSelectedResult1] = useState(null);
  const [selectedResult2, setSelectedResult2] = useState(null);
  const [routeData, setRouteData] = useState([]); // To store route information
  const [errorMessage, setErrorMessage] = useState('');

  const data = datajson.cities;

  useEffect(() => {
    if (selectedResult1 && selectedResult2) {
      triggerApiCall();
    }
  }, [selectedResult1, selectedResult2]);

  // Filter data for the first search bar
  const handleSearch1 = (query) => {
    setSearchQuery1(query);
    setFilteredData1(
      data.filter((item) =>
        item.toLowerCase().includes(query.toLowerCase().replace(/\s/g, ''))
      )
    );
  };

  // Filter data for the second search bar
  const handleSearch2 = (query) => {
    setSearchQuery2(query);
    setFilteredData2(
      data.filter((item) =>
        item.toLowerCase().includes(query.toLowerCase().replace(/\s/g, ''))
      )
    );
  };

  // Trigger API call after both selections are made
  const triggerApiCall = async () => {
    console.log(selectedResult1);
    console.log(selectedResult2);
    if (selectedResult1 && selectedResult2) {
      try {
        const response = await axios.get('http://127.0.0.1:5000/self_yen', {
          params: { source: selectedResult1, target: selectedResult2, k: 5 },
        });
        console.log(response.data.data);
        setRouteData(response.data.data); // Assuming the API returns the structured data
        setErrorMessage('');
      } catch (error) {
        console.error('Error fetching route data:', error);
        setErrorMessage('Failed to fetch route data.');
      }
    }
  };

  // Handle selection
  const handleSelect1 = (result) => {
    console.log(result);
    setSelectedResult1(result);
    // await triggerApiCall();
  };

  const handleSelect2 = (result) => {
    console.log(result);
    setSelectedResult2(result);
    // await triggerApiCall();
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Travel Route Planner</h1>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '20px' }}>
        {/* First Search Bar */}
        <div>
          <input
            type="text"
            placeholder="Search for your starting city..."
            value={searchQuery1}
            onChange={(e) => handleSearch1(e.target.value)}
            style={{
              padding: '10px',
              width: '300px',
              fontSize: '16px',
            }}
          />
          <ul
            style={{
              border: '1px solid #ccc',
              padding: '10px',
              marginTop: '5px',
              maxHeight: '150px',
              overflowY: 'auto',
              listStyleType: 'none',
            }}
          >
            {filteredData1.map((item, index) => (
              <li
                key={index}
                style={{
                  cursor: 'pointer',
                  color: selectedResult1 === item ? 'blue' : 'black',
                }}
                onClick={() => handleSelect1(item)}
              >
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Second Search Bar */}
        <div>
          <input
            type="text"
            placeholder="Search for your destination city..."
            value={searchQuery2}
            onChange={(e) => handleSearch2(e.target.value)}
            style={{
              padding: '10px',
              width: '300px',
              fontSize: '16px',
            }}
          />
          <ul
            style={{
              border: '1px solid #ccc',
              padding: '10px',
              marginTop: '5px',
              maxHeight: '150px',
              overflowY: 'auto',
              listStyleType: 'none',
            }}
          >
            {filteredData2.map((item, index) => (
              <li
                key={index}
                style={{
                  cursor: 'pointer',
                  color: selectedResult2 === item ? 'blue' : 'black',
                }}
                onClick={() => handleSelect2(item)}
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Display Route Data */}
      <div style={{ marginTop: '20px' }}>
        <h2>Route Details:</h2>
        {errorMessage ? (
          <p style={{ color: 'red' }}>{errorMessage}</p>
        ) : routeData.length > 0 ? (
          routeData.map((routes, routeIndex) => (
            <div
              key={routeIndex}
              style={{
                border: '1px solid #ccc',
                marginBottom: '20px',
                padding: '10px',
                borderRadius: '5px',
              }}
            >
              <h3>Route Option {routeIndex + 1}</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Previous City
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Next City
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Transport
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Route ID
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Previous Station
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Next Station
                    </th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>
                      Duration
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {routes.map((route, index) => (
                    <tr key={index}>
                      {route.map((data, idx) => (
                        <td
                          key={idx}
                          style={{
                            border: '1px solid #ccc',
                            padding: '8px',
                          }}
                        >
                          {data}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))
        ) : (
          <p>No route data available.</p>
        )}
      </div>
    </div>
  );
};

export default App;
