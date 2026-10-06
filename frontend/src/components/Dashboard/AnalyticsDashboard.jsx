import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import gsap from 'gsap';
import { Brain, Database, CheckCircle, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';

// Data from the CampusFAQ-50K dataset and model evaluation
const modelComparisonData = [
  { intent: 'Course Info', LogReg: 0.99, SVM: 1.0 },
  { intent: 'Prerequisites', LogReg: 1.0, SVM: 1.0 },
  { intent: 'Attendance', LogReg: 1.0, SVM: 1.0 },
  { intent: 'Exams', LogReg: 0.98, SVM: 0.99 },
  { intent: 'Grading', LogReg: 1.0, SVM: 1.0 },
];

const datasetDistribution = [
  { name: 'course_subject_info', value: 12500 },
  { name: 'course_prerequisite', value: 10000 },
  { name: 'attendance_rules', value: 9500 },
  { name: 'exam_schedule', value: 10500 },
  { name: 'grading_rules', value: 7500 },
];

const COLORS = ['#D4AF37', '#E5E4E2', '#8F7A26', '#4CAF50', '#808080'];

export default function AnalyticsDashboard() {
  const [health, setHealth] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/health');
        setHealth(res.data);
      } catch (err) {
        setHealth({ status: 'offline', service: 'CampusNLP Engine' });
      }
    };
    fetchHealth();
  }, []);

  useEffect(() => {
    if (health) {
      gsap.fromTo('.anim-item', 
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power2.out' }
      );
    }
  }, [health]);

  const StatCard = ({ icon: Icon, title, value, color = "var(--accent-gold)" }) => (
    <div className="anim-item glass-panel" style={{ padding: '24px', flex: '1 1 200px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <Icon size={24} color={color} />
        <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{title}</h3>
      </div>
      <div style={{ fontSize: '1.8rem', fontWeight: 600 }}>{value}</div>
    </div>
  );

  return (
    <div ref={containerRef} style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '40px' }}>
      <div className="anim-item" style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 300, marginBottom: '8px', letterSpacing: '0.5px' }}>Model & Data Analytics</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Performance metrics and distribution data for the CampusFAQ-50K NLP Engine.</p>
      </div>

      {!health ? (
        <div style={{ color: 'var(--text-secondary)' }}>Connecting to Engine...</div>
      ) : (
        <>
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '32px' }}>
            <StatCard icon={Database} title="Dataset Size" value="50,000" />
            <StatCard icon={BarChart2} title="Vocabulary Size (TF-IDF)" value="2,418" />
            <StatCard icon={Brain} title="Active Classifier" value="LogReg" />
            <StatCard icon={CheckCircle} title="Global F1-Score" value="0.99" />
          </div>

          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {/* Chart 1: Model Comparison (F1 Scores) */}
            <div className="anim-item glass-panel" style={{ flex: '2 1 500px', padding: '24px', height: '350px' }}>
              <h3 style={{ marginBottom: '24px', color: 'var(--text-secondary)', fontWeight: 500 }}>Model Comparison: F1-Scores by Intent</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modelComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="intent" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis domain={[0.95, 1.0]} stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }} />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <Bar dataKey="LogReg" fill="var(--accent-gold)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="SVM" fill="var(--text-primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Chart 2: Dataset Distribution */}
            <div className="anim-item glass-panel" style={{ flex: '1 1 350px', padding: '24px', height: '350px' }}>
              <h3 style={{ marginBottom: '24px', color: 'var(--text-secondary)', fontWeight: 500 }}>Dataset Intent Distribution</h3>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={datasetDistribution}
                    cx="50%"
                    cy="45%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {datasetDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)', borderRadius: '8px' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
