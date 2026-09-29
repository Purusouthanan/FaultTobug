import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Play, Search, Network, Code2, FlaskConical } from 'lucide-react';
import type { Incident, Execution } from '../types';

export default function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [executions, setExecutions] = useState<Execution[]>([]);

  const fetchIncident = () => {
    fetch(`http://localhost:8000/incidents/${id}`)
      .then(res => res.json())
      .then(data => setIncident(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
      
    fetch(`http://localhost:8000/incidents/${id}/executions`)
      .then(res => res.json())
      .then(data => setExecutions(data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleAction = async (action: string) => {
    setProcessing(true);
    try {
      await fetch(`http://localhost:8000/incidents/${id}/${action}`, { method: 'POST' });
      fetchIncident();
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return <div className="p-12 text-center"><div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin inline-block"></div></div>;
  }

  if (!incident) {
    return <div className="text-red-400">Incident not found</div>;
  }

  const steps = [
    { id: 'OPEN', label: 'Reported', icon: Search },
    { id: 'ANALYZED', label: 'Analyzed', icon: Network },
    { id: 'REPRODUCED', label: 'Reproduced', icon: Play },
    { id: 'TEST_GENERATED', label: 'Generated', icon: Code2 },
    { id: 'TEST_EXECUTED', label: 'Executed', icon: FlaskConical },
  ];

  const currentStepIndex = steps.findIndex(s => s.id === incident.status);

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <Link to="/incidents" className="inline-flex items-center text-gray-400 hover:text-blue-400 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Incidents
      </Link>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Incident #{incident.id}</h1>
            <p className="text-gray-300 text-lg">{incident.description}</p>
          </div>
          <span className="px-4 py-1.5 rounded-full text-sm font-semibold bg-gray-800 border border-gray-700 text-gray-200">
            {incident.status.replace('_', ' ')}
          </span>
        </div>

        {/* Pipeline Visualizer */}
        <div className="relative pt-8 pb-4">
          <div className="absolute top-12 left-[10%] right-[10%] h-1 bg-gray-800 rounded-full">
            <div 
              className="h-full bg-blue-500 rounded-full transition-all duration-1000 ease-out" 
              style={{ width: `${(Math.max(0, currentStepIndex) / (steps.length - 1)) * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between relative z-10">
            {steps.map((step, idx) => {
              const isPast = currentStepIndex >= idx;
              const isCurrent = currentStepIndex === idx;
              const Icon = step.icon;
              return (
                <div key={step.id} className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500 ${
                    isCurrent
                      ? 'bg-blue-600 border-blue-400 text-white shadow-[0_0_20px_rgba(59,130,246,0.8)] ring-4 ring-blue-500/20 animate-pulse'
                      : isPast 
                        ? 'bg-blue-600 border-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]' 
                        : 'bg-gray-900 border-gray-700 text-gray-500'
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`mt-3 text-xs font-semibold ${isCurrent ? 'text-blue-300 font-bold' : isPast ? 'text-blue-400' : 'text-gray-500'}`}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex gap-4 p-4 bg-gray-900/50 rounded-xl border border-gray-800">
        <button 
          onClick={() => handleAction('analyze')}
          disabled={processing || incident.status !== 'OPEN'}
          className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          1. Analyze
        </button>
        <button 
          onClick={() => handleAction('reproduce')}
          disabled={processing || incident.status !== 'ANALYZED'}
          className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          2. Reproduce
        </button>
        <button 
          onClick={() => handleAction('generate-test')}
          disabled={processing || incident.status !== 'REPRODUCED'}
          className="flex-1 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          3. Generate Test
        </button>
        <button 
          onClick={() => handleAction('execute')}
          disabled={processing || incident.status !== 'TEST_GENERATED'}
          className="flex-1 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          4. Execute
        </button>
      </div>

      {/* Structured Extracted Data */}
      {incident.failure_category && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Network className="w-5 h-5 text-blue-400" /> Analysis Results
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Category</span><span className="text-gray-200 font-medium">{incident.failure_category}</span></div>
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Role</span><span className="text-gray-200 font-medium">{incident.extracted_role}</span></div>
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Action</span><span className="text-gray-200 font-medium">{incident.extracted_action}</span></div>
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Endpoint</span><span className="text-gray-200 font-medium">{incident.extracted_method} {incident.extracted_endpoint}</span></div>
              <div className="flex justify-between border-b border-gray-800 pb-2"><span className="text-gray-400">Expected</span><span className="text-gray-200 font-medium text-green-400">{incident.expected_result}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Actual</span><span className="text-gray-200 font-medium text-red-400">{incident.actual_result}</span></div>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Play className="w-5 h-5 text-indigo-400" /> Reproduction Steps
            </h3>
            {incident.reproduction_steps ? (
              <pre className="text-xs bg-gray-950 p-4 rounded-lg overflow-x-auto text-gray-300 border border-gray-800 h-64">
                {JSON.stringify(JSON.parse(incident.reproduction_steps), null, 2)}
              </pre>
            ) : (
              <p className="text-gray-600 italic">Not reproduced yet.</p>
            )}
          </div>
        </div>
      )}

      {/* Generated Code */}
      {incident.generated_test_code && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Code2 className="w-5 h-5 text-purple-400" /> Generated Pytest Suite
          </h3>
          <pre className="text-xs bg-[#0d1117] p-6 rounded-lg overflow-x-auto text-blue-300 border border-gray-800 shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] font-mono">
            {incident.generated_test_code}
          </pre>
        </div>
      )}

      {/* Execution Results */}
      {executions.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-green-400" /> Execution History
          </h3>
          <div className="space-y-4">
            {executions.map((exec, idx) => (
              <div key={exec.id} className="border border-gray-800 rounded-lg overflow-hidden">
                <div className="bg-gray-950 px-4 py-3 flex justify-between items-center border-b border-gray-800">
                  <span className="text-gray-400 text-sm">Run #{executions.length - idx}</span>
                  <div className="flex gap-4">
                    <span className="text-gray-400 text-sm">{exec.execution_time.toFixed(2)}s</span>
                    <span className={`text-sm font-bold ${exec.status === 'PASS' ? 'text-green-400' : 'text-red-400'}`}>
                      {exec.status}
                    </span>
                  </div>
                </div>
                <pre className="text-xs p-4 text-gray-400 max-h-48 overflow-y-auto">
                  {exec.logs}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
