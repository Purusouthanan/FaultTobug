import { useEffect, useState } from 'react';
import { FlaskConical, Play, CheckCircle2, XCircle } from 'lucide-react';
import type { Execution, Test } from '../types';

export default function RegressionSuite() {
  const [tests, setTests] = useState<Test[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchData = () => {
    Promise.all([
      fetch('http://localhost:8000/regression/tests').then(r => r.json()),
      fetch('http://localhost:8000/regression/suite/executions').then(r => r.json())
    ])
    .then(([testsData, execsData]) => {
      setTests(testsData);
      setExecutions(execsData);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const runSuite = async () => {
    setRunning(true);
    try {
      await fetch('http://localhost:8000/regression/suite/execute', { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <FlaskConical className="w-8 h-8 text-green-500" />
            Regression Suite Repository
          </h1>
          <p className="text-gray-400 mt-2">Manage and execute the accumulated regression tests.</p>
        </div>
        <button 
          onClick={runSuite}
          disabled={running || tests.length === 0}
          className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg font-medium transition-colors shadow-lg shadow-green-900/20"
        >
          {running ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <Play className="w-5 h-5 fill-current" />
          )}
          {running ? 'Executing Suite...' : 'Run Full Suite'}
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-bold text-white">Registered Tests ({tests.length})</h2>
          <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
            {tests.length === 0 && !loading && (
              <div className="p-8 text-center text-gray-500">No regression tests registered yet. Generate tests from incidents first!</div>
            )}
            <div className="divide-y divide-gray-800">
              {tests.map(test => (
                <div key={test.id} className="p-4 hover:bg-gray-800/30 transition-colors">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-gray-200">Incident #{test.incident_id} Regression</span>
                    <span className="text-xs text-gray-500 bg-gray-950 px-2 py-1 rounded border border-gray-800">Test ID: {test.id}</span>
                  </div>
                  <pre className="text-xs text-blue-400/70 truncate">{test.test_code.split('\n')[1]}</pre>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-xl font-bold text-white">Execution History</h2>
          <div className="space-y-4">
            {executions.length === 0 && !loading && (
              <div className="p-8 bg-gray-900 rounded-2xl border border-gray-800 text-center text-gray-500 shadow-xl">No history available.</div>
            )}
            {executions.map(exec => (
              <div key={exec.id} className="bg-gray-900 border border-gray-800 rounded-2xl p-5 shadow-xl">
                <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-800">
                  <div className="text-gray-400 text-sm">Suite Run #{exec.id}</div>
                  <div className="text-gray-500 text-xs">{new Date(exec.executed_at).toLocaleString()}</div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-950 rounded-lg border border-gray-800">
                    <div className="text-gray-500 text-xs mb-1">Passed</div>
                    <div className="text-2xl font-bold text-green-400 flex justify-center items-center gap-1">
                      <CheckCircle2 className="w-5 h-5" /> {exec.total_passed}
                    </div>
                  </div>
                  <div className="text-center p-3 bg-gray-950 rounded-lg border border-gray-800">
                    <div className="text-gray-500 text-xs mb-1">Failed</div>
                    <div className="text-2xl font-bold text-red-400 flex justify-center items-center gap-1">
                      <XCircle className="w-5 h-5" /> {exec.total_failed}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
