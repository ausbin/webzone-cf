import React, { useState, useEffect } from 'react';
import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Label, Legend } from 'recharts';
import './App.css';

interface AppProps {
  incidentsUrl: string,
  incidentsByMonthCsvUrl: string,
  incidentsByHourCsvUrl: string,
}

interface YearIncidents {
  by_month: number[],
  by_hour: number[],
}

interface Incidents {
  start_year: number,
  start_month: number,
  end_year: number,
  end_month: number,
  year_incidents: {[year: number]: YearIncidents}
  last_updated: string,
  offense_code: string,
}

function pastYears(incidents: Incidents) {
  return Array.from({length: incidents.end_year-incidents.start_year},
                    (_, i) => (<span className="App-pastyear" key={i}><strong>{(incidents.start_year + i) + ((i === 0 && incidents.start_month > 0)? '*' : '')}:</strong>&nbsp;
                               {incidents.year_incidents[incidents.start_year + i]
                                         .by_month
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

function incidentsToByMonthChartData(incidents: Incidents) {
  return Array.from({length: incidents.end_year-incidents.start_year+1},
                    (_, i) => incidents.start_year + i)
              .flatMap(year => incidents.year_incidents[year]
                                        .by_month
                                        .map((month_count, month_idx) =>
                                             ({name: withinRange(year, month_idx, incidents)
                                                     ? monthIdxToName(month_idx, true) + ' ' + year
                                                     : null,
                                               count: month_count}))
                                        .filter(datapt => datapt.name !== null));
}

function incidentsToByHourChartData(incidents: Incidents) {
  return Array.from({length: 24}, (_, hour) => {
    let ret: any = {};
    for (let year = incidents.start_year; year <= incidents.end_year; year++) {
      ret['year' + year] = incidents.year_incidents[year].by_hour[hour];
    }
    ret['hour'] = (hour < 12)? ((hour === 0)? (hour+12) : hour) + " AM" : ((hour === 12)? hour : (hour-12)) + " PM";
    return ret;
  });
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
    const byMonthChartData = incidentsToByMonthChartData(incidents);
    const byMonthChart = (
      <AreaChart width={512} height={256} data={byMonthChartData} margin={{top: 0, right: 0, bottom: 15, left: 0}}>
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

    const byHourChartData = incidentsToByHourChartData(incidents);
    // Using the print tertiary colors from https://brand.gatech.edu/our-look/colors
    // because the "web-only" ones are UGLY
    const yearFills = ['#5F249F', '#64CCC9', '#FFCD00', '#3A5DAE', '#A4D233', '#E04F39', '#008C95'];
    const byHourAreas = Array.from({length: incidents.end_year-incidents.start_year+1},
                                   (_, i) => incidents.start_year + i)
                             .map((year, i) => (<Area key={year} type="step" name={"Calls in " + year} dataKey={"year" + year} stroke="none" fill={yearFills[i % yearFills.length]} stackId="1" />));
    const byHourChart = (
      <AreaChart width={512} height={300} data={byHourChartData} margin={{top: 0, right: 0, bottom: 30, left: 0}}>
        {byHourAreas}
        <CartesianGrid stroke="gray" strokeDasharray="2 2" />
        <XAxis dataKey="hour">
          <Label value="Hour" position="insideBottom" offset={-55} />
        </XAxis>
        <YAxis>
          <Label value="Mental Health Calls Reported" position="insideLeft" angle={-90} offset={10} style={{textAnchor: 'middle'}} />
        </YAxis>
        <Tooltip />
        <Legend />
      </AreaChart>
    );

    return (
      <div className="App">
          <p>Times the Georgia Tech Police Department responded to a mental health incident in <strong>{incidents.end_year}</strong>:</p>
          <p className="App-counter">{incidents.year_incidents[incidents.end_year].by_month.reduce((a,b) => a+b, 0)}</p>
          <p>Past years: {pastYears(incidents)}</p>
          <p>Month-by-month statistics:</p>
          <div className="chart">{byMonthChart}</div>
          <p className="App-lilskip">Hour-by-hour statistics:</p>
          <div className="chart">{byHourChart}</div>
          <footer className="App-footer">{(incidents.start_month > 0)? ('* Data for ' + incidents.start_year + ' begins in ' + monthIdxToName(incidents.start_month, false) + '. ') : ''}last updated {incidents.last_updated}. download csv: <a href={props.incidentsByMonthCsvUrl}>by month</a>, <a href={props.incidentsByHourCsvUrl}>by hour</a>. <a href="https://police.gatech.edu/crime-logs-and-map">original data source</a> (use "Offense Code" {incidents.offense_code}). <a href="https://github.com/ausbin/gtpd-monitor">source code</a></footer>
      </div>
    );

  }
}

export default App;

// vim: set ts=2 sw=2 :
