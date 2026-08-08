import { useEffect, useState } from 'react'

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...')

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setBackendStatus(data.status === 'ok' ? 'Connected' : 'Error'))
      .catch(() => setBackendStatus('Disconnected'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-4 text-blue-400">Incident-to-Regression Platform</h1>
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">System Status</h2>
        
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-400">Frontend:</span>
          <span className="text-green-400 font-medium">Running</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Backend API:</span>
          <span className={`font-medium ${
            backendStatus === 'Connected' ? 'text-green-400' : 
            backendStatus === 'Checking...' ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {backendStatus}
          </span>
        </div>
      </div>
    </div>
  )
}

export default App
