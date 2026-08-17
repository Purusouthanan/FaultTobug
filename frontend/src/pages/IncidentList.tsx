import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowRight, ServerCrash, Activity } from 'lucide-react';
import { Incident } from '../types';

export default function IncidentList() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/incidents/')
      .then(res => res.json())
      .then(data => {
        setIncidents(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'OPEN': return 'bg-gray-800 text-gray-300 border-gray-700';
      case 'ANALYZED': return 'bg-blue-900/50 text-blue-300 border-blue-800';
      case 'REPRODUCED': return 'bg-indigo-900/50 text-indigo-300 border-indigo-800';
      case 'TEST_GENERATED': return 'bg-purple-900/50 text-purple-300 border-purple-800';
      case 'TEST_EXECUTED': return 'bg-green-900/50 text-green-300 border-green-800';
      case 'ERROR': return 'bg-red-900/50 text-red-300 border-red-800';
      default: return 'bg-gray-800 text-gray-400 border-gray-700';
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-blue-500" />
            Incidents
          </h1>
          <p className="text-gray-400 mt-2">Manage and process production incidents through the pipeline.</p>
        </div>
      </header>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 flex justify-center items-center">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-950/50 border-b border-gray-800">
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">ID</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Description</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Category</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                  <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {incidents.map((incident) => (
                  <tr key={incident.id} className="hover:bg-gray-800/30 transition-colors group">
                    <td className="p-4 text-sm font-medium text-gray-400">#{incident.id}</td>
                    <td className="p-4 text-sm text-gray-200">
                      <div className="flex items-center gap-2">
                        {incident.status === 'ERROR' ? <ServerCrash className="w-4 h-4 text-red-500" /> : <Activity className="w-4 h-4 text-blue-500" />}
                        <span className="truncate max-w-md block">{incident.description}</span>
                      </div>
                    </td>
                    <td className="p-4 text-sm text-gray-400">
                      {incident.failure_category || <span className="italic text-gray-600">Pending Analysis</span>}
                    </td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(incident.status)}`}>
                        {incident.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <Link 
                        to={`/incidents/${incident.id}`}
                        className="inline-flex items-center justify-center p-2 rounded-lg bg-gray-800 hover:bg-blue-600 text-gray-400 hover:text-white transition-colors group-hover:shadow-lg"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
