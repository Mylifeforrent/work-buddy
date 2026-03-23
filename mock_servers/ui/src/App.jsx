import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  Card,
  Form,
  Input,
  Button,
  Table,
  Space,
  Tag,
  Typography,
  Descriptions,
  List,
  Avatar,
  Badge,
  Statistic,
  Row,
  Col,
  Divider,
  message,
  theme
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  DashboardOutlined,
  UnorderedListOutlined,
  FormOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SearchOutlined,
  FileTextOutlined
} from '@ant-design/icons';

const { Header, Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;
const { useToken } = theme;

// --- Auth Context ---
const AuthContext = createContext(null);

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const savedUser = sessionStorage.getItem('mockUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = (username) => {
    const userData = { username, name: `User ${username}`, loginTime: new Date().toISOString() };
    setUser(userData);
    sessionStorage.setItem('mockUser', JSON.stringify(userData));
    return true;
  };

  const logout = () => {
    setUser(null);
    sessionStorage.removeItem('mockUser');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// --- Login Page ---
const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    // Simulate login delay
    await new Promise(resolve => setTimeout(resolve, 500));
    login(values.username);
    message.success('Login successful!');
    navigate('/dashboard');
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #1890ff 0%, #722ed1 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3} style={{ marginBottom: 0 }}>Mock App Login</Title>
          <Text type="secondary">Enter any credentials to test</Text>
        </div>
        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Username (any value)" id="username" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password (any value)" id="password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block id="submit">
              Sign In
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

// --- Protected Route ---
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <Text>Loading...</Text>
    </div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// --- Dashboard Page ---
const DashboardPage = () => {
  const { user } = useAuth();
  const { token } = useToken();

  const stats = [
    { title: 'Total Tasks', value: 156, suffix: 'items' },
    { title: 'Completed', value: 128, suffix: 'items' },
    { title: 'In Progress', value: 23, suffix: 'items' },
    { title: 'Pending', value: 5, suffix: 'items' },
  ];

  return (
    <div>
      <Title level={4}>Dashboard</Title>
      <Paragraph type="secondary">
        Welcome back, {user?.name || 'User'}! Here's your overview.
      </Paragraph>

      <Row gutter={16} style={{ marginTop: 16, marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                suffix={stat.suffix}
                valueStyle={{ color: index === 3 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="Recent Activity">
        <List
          dataSource={[
            { text: 'Completed task PROJ-123', time: '2 hours ago', status: 'success' },
            { text: 'Created new ticket PROJ-156', time: '5 hours ago', status: 'info' },
            { text: 'Updated documentation', time: '1 day ago', status: 'success' },
            { text: 'Reviewed pull request #42', time: '2 days ago', status: 'success' },
          ]}
          renderItem={item => (
            <List.Item>
              <List.Item.Meta
                avatar={<Avatar icon={item.status === 'success' ? <CheckCircleOutlined /> : <FileTextOutlined />} />}
                title={item.text}
                description={item.time}
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

// --- Data List Page ---
const DataListPage = () => {
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (status) => {
      const colors = { 'Active': 'green', 'Pending': 'orange', 'Inactive': 'red' };
      return <Tag color={colors[status]}>{status}</Tag>;
    }},
    { title: 'Created', dataIndex: 'created', key: 'created' },
    { title: 'Action', key: 'action', render: () => (
      <Space>
        <Button type="link" size="small">View</Button>
        <Button type="link" size="small">Edit</Button>
      </Space>
    )},
  ];

  const data = [
    { key: '1', id: '001', title: 'Sample Data Item 1', status: 'Active', created: '2024-01-15' },
    { key: '2', id: '002', title: 'Sample Data Item 2', status: 'Pending', created: '2024-01-16' },
    { key: '3', id: '003', title: 'Sample Data Item 3', status: 'Active', created: '2024-01-17' },
    { key: '4', id: '004', title: 'Sample Data Item 4', status: 'Inactive', created: '2024-01-18' },
    { key: '5', id: '005', title: 'Sample Data Item 5', status: 'Active', created: '2024-01-19' },
  ];

  return (
    <div>
      <Title level={4}>Data List</Title>
      <Paragraph type="secondary">
        Browse and manage data records with Ant Design Table component.
      </Paragraph>

      <Card style={{ marginTop: 16 }}>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <Input.Search placeholder="Search records..." style={{ width: 300 }} />
          <Button type="primary">Add New</Button>
        </div>
        <Table columns={columns} dataSource={data} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
};

// --- Form Page ---
const FormPage = () => {
  const [form] = Form.useForm();

  const onFinish = (values) => {
    console.log('Form values:', values);
    message.success('Form submitted successfully!');
  };

  return (
    <div>
      <Title level={4}>Form Submission</Title>
      <Paragraph type="secondary">
        Test form inputs and validation with Ant Design Form component.
      </Paragraph>

      <Card style={{ marginTop: 16, maxWidth: 600 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item name="name" label="Full Name" rules={[{ required: true }]}>
            <Input placeholder="Enter your name" />
          </Form.Item>

          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input placeholder="Enter your email" />
          </Form.Item>

          <Form.Item name="phone" label="Phone Number">
            <Input placeholder="Enter phone number" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Enter description" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">Submit</Button>
              <Button onClick={() => form.resetFields()}>Reset</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

// --- Analytics Page ---
const AnalyticsPage = () => {
  const chartData = [
    { month: 'Jan', value: 30 },
    { month: 'Feb', value: 45 },
    { month: 'Mar', value: 28 },
    { month: 'Apr', value: 60 },
    { month: 'May', value: 55 },
    { month: 'Jun', value: 80 },
  ];

  return (
    <div>
      <Title level={4}>Analytics</Title>
      <Paragraph type="secondary">
        View metrics and analytics data.
      </Paragraph>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="Performance Metrics">
            <div style={{ height: 200, display: 'flex', alignItems: 'flex-end', gap: 8 }}>
              {chartData.map((item, i) => (
                <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                  <div style={{
                    height: `${item.value * 2}px`,
                    background: 'linear-gradient(180deg, #1890ff 0%, #69c0ff 100%)',
                    borderRadius: 4
                  }} />
                  <Text type="secondary" style={{ fontSize: 12 }}>{item.month}</Text>
                </div>
              ))}
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Status Overview">
            <Descriptions column={1}>
              <Descriptions.Item label="Uptime">99.9%</Descriptions.Item>
              <Descriptions.Item label="Response Time">45ms</Descriptions.Item>
              <Descriptions.Item label="Error Rate">0.1%</Descriptions.Item>
              <Descriptions.Item label="Active Users">1,234</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// --- Main Layout ---
const MainLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/list', icon: <UnorderedListOutlined />, label: 'Data List' },
    { key: '/form', icon: <FormOutlined />, label: 'Form' },
    { key: '/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
  ];

  const handleMenuClick = (e) => {
    navigate(e.key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    message.info('Logged out successfully');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="light">
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <Title level={4} style={{ margin: 0 }}>Mock App</Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <Text strong>Work Buddy Test App</Text>
          <Space>
            <Text type="secondary">Welcome, {user?.name}</Text>
            <Button icon={<LogoutOutlined />} onClick={handleLogout}>Logout</Button>
          </Space>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8, minHeight: 280 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

// --- App Component ---
function App() {
  const toolId = window.TOOL_ID || 'react-app';

  // For mock tool pages (Jira, Confluence, etc.), render simple mock UI
  if (toolId !== 'react-app') {
    return (
      <div style={{ padding: 24, minHeight: '100vh', background: '#f5f5f5' }}>
        <Card>
          <Title level={3}>Mock {toolId.toUpperCase()} Service</Title>
          <Paragraph>This is a mock UI for {toolId}. For full testing, use the React App mode.</Paragraph>
          <Form>
            <Form.Item label="Search">
              <Input.Search placeholder={`Search in ${toolId}...`} />
            </Form.Item>
          </Form>
          <Button type="primary">Mock Action</Button>
        </Card>
      </div>
    );
  }

  // Full React App with Ant Design for testing
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Routes>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/list" element={<DataListPage />} />
                    <Route path="/form" element={<FormPage />} />
                    <Route path="/analytics" element={<AnalyticsPage />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;