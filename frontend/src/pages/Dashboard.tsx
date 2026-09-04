import { useEffect, useState } from 'react';
import { Activity, CheckCircle2, XCircle, TrendingUp, ShieldAlert, Cpu } from 'lucide-react';
import type { Incident } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    analyzed: 0,
    reproduced: 0,
    generated: 0,
    executed: 0,
  });

  useEffect(() => {
    fetch('http://localhost:8000/incidents/')
      .then(res => res.json())
      .then((data: Incident[]) => {
        const counts = {
          total: data.length,
          open: data.filter((i: Incident) => i.status === 'OPEN').length,
          analyzed: data.filter((i: Incident) => i.status === 'ANALYZED').length,
          reproduced: data.filter((i: Incident) => i.status === 'REPRODUCED').length,
          generated: data.filter((i: Incident) => i.status === 'TEST_GENERATED').length,
          executed: data.filter((i: Incident) => i.status === 'TEST_EXECUTED').length,
        };
        setStats(counts);
      })
      .catch(err => console.error("Failed to fetch incidents", err));
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
          <Activity className="w-8 h-8 text-blue-500" />
          Command Center
        </h1>
        <p className="text-gray-400 mt-2">Overview of incident processing and regression metrics.</p>
      </header>

      {/* Primary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium">Total Incidents</h3>
            <ShieldAlert className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-4xl font-bold text-white">{stats.total}</p>
          <p className="text-sm text-gray-500 mt-2">Currently tracked in system</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium">Prototype Conversion</h3>
            <TrendingUp className="w-5 h-5 text-green-400" />
          </div>
          <p className="text-4xl font-bold text-white">23.1%</p>
          <p className="text-sm text-green-400 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4" /> 6/26 Incidents Passed
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium">Baseline Conversion</h3>
            <Cpu className="w-5 h-5 text-red-400" />
          </div>
          <p className="text-4xl font-bold text-white">0.0%</p>
          <p className="text-sm text-red-400 mt-2 flex items-center gap-1">
            <XCircle className="w-4 h-4" /> 0/26 Incidents Passed
          </p>
        </div>
      </div>

      {/* Pipeline Status Breakdown */}
      <div>
        <h2 className="text-xl font-bold text-white mb-6">Pipeline Pipeline Queue</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="grid grid-cols-2 md:grid-cols-5 divide-y md:divide-y-0 divide-x-0 md:divide-x divide-gray-800">
            <div className="p-6 text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">Open</p>
              <p className="text-2xl font-bold text-white">{stats.open}</p>
            </div>
            <div className="p-6 text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">Analyzed</p>
              <p className="text-2xl font-bold text-blue-400">{stats.analyzed}</p>
            </div>
            <div className="p-6 text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">Reproduced</p>
              <p className="text-2xl font-bold text-indigo-400">{stats.reproduced}</p>
            </div>
            <div className="p-6 text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">Generated</p>
              <p className="text-2xl font-bold text-purple-400">{stats.generated}</p>
            </div>
            <div className="p-6 text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">Executed</p>
              <p className="text-2xl font-bold text-green-400">{stats.executed}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
