import React, { useState, useEffect } from 'react';
import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Label } from 'recharts';
//import logo from './logo.svg';
import './App.css';

interface AppProps {
  incidentsUrl: string,
}

interface Incidents {
  start_year: number,
  start_month: number,
  end_year: number,
  end_month: number,
  year_incidents: {[year: number]: number[]}
  last_updated: string,
  offense_code: string,
}

function pastYears(incidents: Incidents) {
  return Array.from({length: incidents.end_year-incidents.start_year},
                    (_, i) => (<span className="App-pastyear" key={i}><strong>{(incidents.start_year + i) + ((i === 0 && incidents.start_month > 0)? '*' : '')}:</strong>&nbsp;
                               {incidents.year_incidents[incidents.start_year + i]
                                         .reduce((a,b) => a+b, 0)}</span>));
}

function withinRange(year: number, month_idx: number, incidents: Incidents) {
  return ((year === incidents.start_year && month_idx >= incidents.start_month) || year > incidents.start_year)
         && ((year === incidents.end_year && month_idx <= incidents.end_month) || year < incidents.end_year);
}

function monthIdxToName(month_idx: number, abbrev: boolean) {
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const name = months[month_idx];
  return abbrev? name.substring(0, 3) : name;
}

function incidentsToChartData(incidents: Incidents) {
  return Array.from({length: incidents.end_year-incidents.start_year+1},
                    (_, i) => incidents.start_year + i)
              .flatMap(year => incidents.year_incidents[year]
                                        .map((month_count, month_idx) =>
                                             ({name: withinRange(year, month_idx, incidents)
                                                     ? monthIdxToName(month_idx, true) + ' ' + year
                                                     : null,
                                               count: month_count}))
                                        .filter(datapt => datapt.name !== null));
}

function App(props: AppProps) {
  const [incidents, setIncidents] = useState<Incidents|null>(null);
  const [errorMessage, setErrorMessage] = useState<string|null>(null);

  useEffect(() => {
    if (incidents === null && errorMessage === null) {
      fetch(props.incidentsUrl).then(resp => {
                                if (resp.ok) {
                                  return resp.json();
                                } else {
                                  throw new Error('got status code ' + resp.status);
                                }
                               })
                               .then(data => {
                                 setIncidents(data);
                               })
                               .catch(error => {
                                 setErrorMessage(error.toString());
                               });
    }
  });

  if (incidents === null) {
    return (<div className="App">{errorMessage? errorMessage : <div className="App-loading">loading... <div className="App-bee">🐝</div></div>}</div>);
  } else {
    const chartData = incidentsToChartData(incidents);
    const chart = (
      <AreaChart width={512} height={256} data={chartData} margin={{top: 0, right: 0, bottom: 15, left: 0}}>
        <Area type="step" name="Calls" dataKey="count" stroke="gray" fill="#B3A369" />
        <CartesianGrid stroke="gray" strokeDasharray="2 2" />
        <XAxis dataKey="name">
          <Label value="Month" position="insideBottom" offset={-15} />
        </XAxis>
        <YAxis>
          <Label value="Mental Health Calls Reported" position="insideLeft" angle={-90} offset={10} style={{textAnchor: 'middle'}} />
        </YAxis>
        <Tooltip />
      </AreaChart>
    );

    return (
      <div className="App">
          <p>Times the Georgia Tech Police Department responded to a mental health incident in <strong>{incidents.end_year}</strong>:</p>
          <p className="App-counter">{incidents.year_incidents[incidents.end_year].reduce((a,b) => a+b, 0)}</p>
          <p>Past years: {pastYears(incidents)}</p>
          <p>Month-by-month breakdown:</p>
          <div className="chart">{chart}</div>
          <footer className="App-footer">{(incidents.start_month > 0)? ('* Data for ' + incidents.start_year + ' begins in ' + monthIdxToName(incidents.start_month, false) + '. ') : ''}last updated {incidents.last_updated}. <a href="https://police.gatech.edu/crime-logs-and-map">data source</a> (use "Offense Code" {incidents.offense_code}). <a href="https://github.com/ausbin/gtpd-monitor">source code</a></footer>
      </div>
    );

  }
}

export default App;

// vim: set ts=2 sw=2 :
