import React, { useState, useEffect } from 'react';
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
  last_updated: string,
  year_incidents: {[year: number]: number[]}
}

function pastYears(incidents: Incidents) {
  return Array.from({length: incidents.end_year-incidents.start_year},
                    (_, i) => (<li key={i}><strong>{incidents.start_year + i}:</strong>&nbsp;
                               {incidents.year_incidents[incidents.start_year + i]
                                         .reduce((a,b) => a+b, 0)}</li>));
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
    return (<div className="App">{errorMessage || 'loading...'}</div>);
  } else {
    return (
      <div className="App">
          <p>GTPD Mental Health Calls Reported in <strong>{incidents.end_year}</strong>:</p>
          <p className="App-counter">{incidents.year_incidents[incidents.end_year].reduce((a,b) => a+b, 0)}</p>
          <p>Past years:</p><ol className="App-pastyears">{pastYears(incidents)}</ol>
          <footer className="App-footer">last updated {incidents.last_updated}. <a href="https://police.gatech.edu/crime-logs-and-map">data source</a>. <a href="https://github.com/ausbin/gtpd-counter">source code</a></footer>
      </div>
    );
  }
}

export default App;

// vim: set ts=2 sw=2 :
