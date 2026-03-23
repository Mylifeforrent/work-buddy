import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Activity, 
  Search, 
  FileText, 
  LayoutDashboard, 
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';

// --- SSO Component ---
const MockSSO = () => (
  <div className="flex flex-col items-center justify-center min-h-screen p-4">
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card w-full max-w-md shadow-2xl"
    >
      <div className="flex items-center gap-3 mb-6">
        <ShieldCheck className="text-blue-400 w-8 h-8" />
        <h2 className="text-2xl font-bold">Corporate SSO</h2>
      </div>
      <form action="/login" method="POST" className="space-y-4">
        <div>
          <label className="block text-slate-400 mb-2">Staff ID</label>
          <input type="text" id="username" name="username" className="input" required />
        </div>
        <div>
          <label className="block text-slate-400 mb-2">Password</label>
          <input type="password" id="password" name="password" className="input" required />
        </div>
        <button type="submit" id="submit" className="btn btn-primary w-full mt-4">Sign In</button>
      </form>
    </motion.div>
  </div>
);

// --- Jira Component ---
const MockJira = () => (
  <div className="min-h-screen bg-slate-900 p-8">
    <div className="flex items-center gap-3 mb-8">
      <LayoutDashboard className="jira-blue w-8 h-8" />
      <h1 className="text-2xl font-bold">Jira Service Desktop</h1>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {['Backlog', 'In Progress', 'Done'].map(status => (
        <div key={status} className="card min-h-[400px]">
          <h3 className="text-slate-400 font-semibold mb-4 border-b border-slate-700 pb-2">{status}</h3>
          <div className="space-y-3">
            {[1, 2].map(i => (
              <motion.div 
                whileHover={{ scale: 1.02 }}
                key={i} 
                className="bg-slate-800 p-4 rounded-lg border border-slate-700 cursor-pointer"
              >
                <div className="text-blue-400 text-sm mb-1">PROJ-{i}00{i}</div>
                <div className="text-slate-200">Example Issue {i} - Mock {status} task</div>
              </motion.div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// --- Confluence Component ---
const MockConfluence = () => (
  <div className="min-h-screen bg-slate-900">
    <div className="flex border-b border-slate-700 h-screen">
      <div className="w-64 bg-slate-800 p-6 border-r border-slate-700">
        <div className="flex items-center gap-2 mb-8">
          <FileText className="confluence-blue w-6 h-6" />
          <span className="font-bold">Confluence</span>
        </div>
        <div className="space-y-2">
          {['Technical Specs', 'Onboarding Guide', 'API Documentation', 'Team Notes'].map(p => (
            <div key={p} className="text-slate-400 hover:text-white cursor-pointer py-1">{p}</div>
          ))}
        </div>
      </div>
      <div className="flex-1 p-12 overflow-y-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h1 className="text-4xl font-bold mb-6">Technical Specification V2</h1>
          <div className="prose prose-invert max-w-none text-slate-300 space-y-4">
            <p>This document outlines the architectural changes for the Work Buddy V2 system integration.</p>
            <h2 className="text-2xl font-semibold text-white mt-8">Overview</h2>
            <p>We are migrating multiple service transports to MCP (Model Context Protocol) to enable richer interactions for AI coding assistants.</p>
          </div>
        </motion.div>
      </div>
    </div>
  </div>
);

// --- OpenSearch Component ---
const MockOpenSearch = () => (
  <div className="min-h-screen bg-slate-900 p-6">
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-3">
        <Search className="opensearch-green w-8 h-8" />
        <h1 className="text-2xl font-bold">OpenSearch Dashboards</h1>
      </div>
      <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 text-sm">
        Last 15 minutes
      </div>
    </div>
    <div className="card mb-6">
      <input type="text" className="input" placeholder="Search (e.g. status:500 OR level:ERROR)" />
    </div>
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      <table className="w-full text-left">
        <thead className="bg-slate-900/50 text-slate-400 text-sm">
          <tr>
            <th className="p-4">Timestamp</th>
            <th className="p-4">Level</th>
            <th className="p-4">Message</th>
            <th className="p-4">Service</th>
          </tr>
        </thead>
        <tbody className="text-slate-200">
          {[1, 2, 3, 4, 5].map(i => (
            <tr key={i} className="border-t border-slate-700 hover:bg-slate-700/30">
              <td className="p-4 text-sm text-slate-400">2023-01-01 12:00:0{i}</td>
              <td className="p-4">
                <span className={`px-2 py-0.5 rounded text-xs ${i % 2 === 0 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                  {i % 2 === 0 ? 'ERROR' : 'INFO'}
                </span>
              </td>
              <td className="p-4">Simulation log entry #{i} for test verification</td>
              <td className="p-4 text-slate-400">auth-service</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// --- SpringBoot Admin Component ---
const MockSpringBootAdmin = () => (
  <div className="min-h-screen bg-slate-900 p-8">
    <div className="flex items-center gap-3 mb-8">
      <Activity className="spring-green w-8 h-8" />
      <h1 className="text-2xl font-bold">Spring Boot Admin</h1>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {['auth-service', 'payment-service', 'order-service', 'inventory-service'].map((name, i) => (
        <motion.div 
          key={name}
          whileHover={{ y: -5 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <span className="font-semibold text-slate-200">{name}</span>
            <CheckCircle2 className="text-spring-green w-5 h-5" />
          </div>
          <div className="text-sm text-slate-400">Up since 48h 12m</div>
          <div className="mt-4 pt-4 border-t border-slate-700 text-xs text-blue-400 uppercase tracking-wider font-bold">
            All Systems Operational
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

// --- Grafana Component ---
const MockGrafana = () => (
  <div className="min-h-screen bg-slate-900 p-6">
    <div className="flex items-center gap-3 mb-8">
      <BarChart3 className="grafana-orange w-8 h-8" />
      <h1 className="text-2xl font-bold">Grafana Dashboard</h1>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map(i => (
        <div key={i} className="card h-64 flex flex-col items-center justify-center border-t-4 border-t-grafana-orange">
          <div className="text-slate-400 mb-2">Metric Chart #{i}</div>
          <div className="h-32 w-full bg-slate-800 rounded flex items-end gap-1 p-2">
            {[4, 7, 2, 9, 3, 5, 8].map((h, j) => (
              <div key={j} className="bg-blue-600/40 w-full" style={{ height: `${h * 10}%` }}></div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// --- Main App Component ---
function App() {
  const toolId = window.TOOL_ID || 'sso';

  const renderTool = () => {
    switch (toolId) {
      case 'sso': return <MockSSO />;
      case 'jira': return <MockJira />;
      case 'confluence': return <MockConfluence />;
      case 'opensearch': return <MockOpenSearch />;
      case 'springboot_admin': return <MockSpringBootAdmin />;
      case 'grafana': return <MockGrafana />;
      default: return <MockSSO />;
    }
  };

  return (
    <div className="mock-ui-container">
      {renderTool()}
    </div>
  );
}

export default App;
