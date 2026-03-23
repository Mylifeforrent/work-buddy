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
  theme,
  ConfigProvider,
  Progress,
  Tooltip,
  Spin
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
  FileTextOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  HomeOutlined,
  DatabaseOutlined,
  LineChartOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  SyncOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const stats = [
    { title: 'Total Revenue', value: 52840, prefix: '$', icon: <DollarOutlined />, color: '#52c41a' },
    { title: 'Active Users', value: 2841, suffix: 'users', icon: <TeamOutlined />, color: '#1890ff' },
    { title: 'Total Orders', value: 682, suffix: 'orders', icon: <ShoppingCartOutlined />, color: '#722ed1' },
    { title: 'Growth Rate', value: 12.5, suffix: '%', icon: <RiseOutlined />, color: '#fa8c16' },
  ];

  const recentOrders = [
    { id: 'ORD-001', customer: 'John Smith', amount: 125.00, status: 'completed', date: '2024-01-15' },
    { id: 'ORD-002', customer: 'Sarah Johnson', amount: 89.50, status: 'processing', date: '2024-01-15' },
    { id: 'ORD-003', customer: 'Mike Chen', amount: 245.00, status: 'pending', date: '2024-01-14' },
    { id: 'ORD-004', customer: 'Emily Davis', amount: 67.25, status: 'completed', date: '2024-01-14' },
    { id: 'ORD-005', customer: 'Tom Wilson', amount: 189.00, status: 'completed', date: '2024-01-13' },
  ];

  const statusColors = {
    completed: 'green',
    processing: 'blue',
    pending: 'orange'
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <Spin size="large" tip="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Dashboard</Title>
        <Paragraph type="secondary">
          Welcome back, {user?.name || 'User'}! Here's what's happening with your business today.
        </Paragraph>
      </div>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              hoverable
              style={{ borderRadius: 12, borderLeft: `4px solid ${stat.color}` }}
            >
              <Space direction="vertical" size={0} style={{ width: '100%' }}>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text type="secondary" style={{ fontSize: 13 }}>{stat.title}</Text>
                  <Avatar style={{ backgroundColor: `${stat.color}20`, color: stat.color }} icon={stat.icon} />
                </Space>
                <Title level={2} style={{ margin: 0 }}>
                  {stat.prefix}{stat.value.toLocaleString()}{stat.suffix && <Text type="secondary" style={{ fontSize: 14 }}> {stat.suffix}</Text>}
                </Title>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Charts and Tables */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card
            title={<Space><LineChartOutlined style={{ color: '#1890ff' }} /> Performance Overview</Space>}
            style={{ borderRadius: 12 }}
          >
            <div style={{ height: 250, display: 'flex', alignItems: 'flex-end', gap: 16, padding: '20px 10px' }}>
              {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'].map((month, i) => {
                const heights = [45, 62, 38, 75, 55, 82, 68];
                return (
                  <div key={month} style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{
                      height: `${heights[i]}%`,
                      background: `linear-gradient(180deg, ${token.colorPrimary} 0%, ${token.colorPrimaryBg} 100%)`,
                      borderRadius: '8px 8px 0 0',
                      transition: 'height 0.3s ease',
                      cursor: 'pointer'
                    }} />
                    <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>{month}</Text>
                  </div>
                );
              })}
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card
            title={<Space><TeamOutlined style={{ color: '#722ed1' }} /> User Activity</Text></Space>}
            style={{ borderRadius: 12 }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Active Sessions</Text>
                  <Text strong>1,234</Text>
                </Space>
                <Progress percent={78} size="small" showInfo={false} strokeColor="#52c41a" />
              </div>
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>New Users Today</Text>
                  <Text strong>48</Text>
                </Space>
                <Progress percent={32} size="small" showInfo={false} strokeColor="#1890ff" />
              </div>
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Conversion Rate</Text>
                  <Text strong>24.5%</Text>
                </Space>
                <Progress percent={55} size="small" showInfo={false} strokeColor="#722ed1" />
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Recent Orders */}
      <Card
        title={<Space><DatabaseOutlined style={{ color: '#1890ff' }} /> Recent Orders</Space>}
        style={{ marginTop: 16, borderRadius: 12 }}
        extra={<Button type="link">View All</Button>}
      >
        <List
          dataSource={recentOrders}
          renderItem={item => (
            <List.Item style={{ padding: '12px 0' }}>
              <List.Item.Meta
                avatar={<Avatar style={{ backgroundColor: '#f0f2f5' }} icon={<ShoppingCartOutlined />} />}
                title={<Space><Text strong>{item.id}</Text><Tag color={statusColors[item.status]}>{item.status}</Tag></Space>}
                description={item.customer}
              />
              <Text strong style={{ fontSize: 16 }}>${item.amount.toFixed(2)}</Text>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

// --- Data List Page ---
const DataListPage = () => {
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [loading, setLoading] = useState(false);

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (id) => <Tag color="blue">{id}</Tag>
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (title) => <Text strong>{title}</Text>
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (cat) => <Tag color="purple">{cat}</Tag>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = { 'Active': 'success', 'Pending': 'warning', 'Inactive': 'error' };
        const icons = { 'Active': <CheckCircleOutlined />, 'Pending': <SyncOutlined spin />, 'Inactive': <CloseCircleOutlined /> };
        return <Tag color={colors[status]} icon={icons[status]}>{status}</Tag>;
      }
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress) => <Progress percent={progress} size="small" />
    },
    {
      title: 'Created',
      dataIndex: 'created',
      key: 'created',
      render: (date) => <Text type="secondary">{date}</Text>
    },
    {
      title: 'Actions',
      key: 'action',
      width: 150,
      render: () => (
        <Space>
          <Tooltip title="View">
            <Button type="text" size="small" icon={<EyeOutlined />} style={{ color: '#1890ff' }} />
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="text" size="small" icon={<EditOutlined />} style={{ color: '#52c41a' }} />
          </Tooltip>
          <Tooltip title="Delete">
            <Button type="text" size="small" icon={<DeleteOutlined />} danger />
          </Tooltip>
        </Space>
      )
    },
  ];

  const data = [
    { key: '1', id: '001', title: 'Payment Gateway Integration', category: 'Finance', status: 'Active', progress: 85, created: '2024-01-15' },
    { key: '2', id: '002', title: 'User Authentication Module', category: 'Security', status: 'Active', progress: 100, created: '2024-01-16' },
    { key: '3', id: '003', title: 'Dashboard Analytics', category: 'Analytics', status: 'Pending', progress: 45, created: '2024-01-17' },
    { key: '4', id: '004', title: 'Mobile App Redesign', category: 'Design', status: 'Inactive', progress: 20, created: '2024-01-18' },
    { key: '5', id: '005', title: 'API Rate Limiting', category: 'Backend', status: 'Active', progress: 70, created: '2024-01-19' },
    { key: '6', id: '006', title: 'Email Notification System', category: 'Communication', status: 'Pending', progress: 55, created: '2024-01-20' },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  };

  const hasSelected = selectedRowKeys.length > 0;

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3}>Data Management</Title>
        <Paragraph type="secondary">
          Browse, filter, and manage your data records with advanced table features.
        </Paragraph>
      </div>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Input.Search
              placeholder="Search records..."
              style={{ width: 280 }}
              allowClear
              enterButton
            />
            {hasSelected && (
              <Tag color="blue">{selectedRowKeys.length} items selected</Tag>
            )}
          </Space>
          <Space>
            <Button icon={<SyncOutlined />}>Refresh</Button>
            <Button type="primary" icon={<PlusOutlined />}>Add New Record</Button>
          </Space>
        </div>
        <Table
          columns={columns}
          dataSource={data}
          rowSelection={rowSelection}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} records`
          }}
          loading={loading}
          style={{ borderRadius: 8 }}
        />
      </Card>
    </div>
  );
};

// --- Form Page ---
const FormPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Form values:', values);
    message.success('Form submitted successfully!');
    setLoading(false);
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3}>Form Submission</Title>
        <Paragraph type="secondary">
          Test form inputs and validation with comprehensive form components.
        </Paragraph>
      </div>

      <Row gutter={24}>
        <Col xs={24} lg={14}>
          <Card title="User Information" style={{ borderRadius: 12 }}>
            <Form
              form={form}
              layout="vertical"
              onFinish={onFinish}
              initialValues={{ priority: 'normal', notifications: true }}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="firstName" label="First Name" rules={[{ required: true }]}>
                    <Input placeholder="Enter first name" size="large" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="lastName" label="Last Name" rules={[{ required: true }]}>
                    <Input placeholder="Enter last name" size="large" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item name="email" label="Email Address" rules={[{ required: true, type: 'email' }]}>
                <Input prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} placeholder="Enter your email" size="large" />
              </Form.Item>

              <Form.Item name="phone" label="Phone Number">
                <Input prefix={<Text style={{ color: '#bfbfbf' }}>+1</Text>} placeholder="(555) 123-4567" size="large" />
              </Form.Item>

              <Form.Item name="department" label="Department">
                <Input placeholder="e.g., Engineering, Marketing" size="large" />
              </Form.Item>

              <Form.Item name="description" label="Description">
                <Input.TextArea rows={4} placeholder="Enter additional details..." showCount maxLength={500} />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={loading} size="large">
                    Submit Form
                  </Button>
                  <Button onClick={() => form.resetFields()} size="large">
                    Reset
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card title="Form Guidelines" style={{ borderRadius: 12, background: '#fafafa' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <Text>All fields marked with * are required</Text>
              </div>
              <div>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <Text>Email must be a valid email address</Text>
              </div>
              <div>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <Text>Description is limited to 500 characters</Text>
              </div>
              <div>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <Text>Phone number is optional</Text>
              </div>
            </Space>
          </Card>

          <Card title="Recent Submissions" style={{ borderRadius: 12, marginTop: 16 }}>
            <List
              size="small"
              dataSource={[
                { name: 'John Smith', time: '2 hours ago' },
                { name: 'Sarah Johnson', time: '5 hours ago' },
                { name: 'Mike Chen', time: '1 day ago' },
              ]}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                    title={item.name}
                    description={item.time}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// --- Analytics Page ---
const AnalyticsPage = () => {
  const [timeRange, setTimeRange] = useState('week');

  const chartData = [
    { month: 'Jan', value: 30, target: 25 },
    { month: 'Feb', value: 45, target: 40 },
    { month: 'Mar', value: 28, target: 35 },
    { month: 'Apr', value: 60, target: 50 },
    { month: 'May', value: 55, target: 55 },
    { month: 'Jun', value: 80, target: 60 },
  ];

  const metrics = [
    { label: 'Total Page Views', value: '124,892', change: '+12.5%', up: true },
    { label: 'Unique Visitors', value: '45,231', change: '+8.2%', up: true },
    { label: 'Bounce Rate', value: '32.4%', change: '-5.1%', up: false },
    { label: 'Avg. Session', value: '4m 32s', change: '+2.3%', up: true },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3}>Analytics Dashboard</Title>
        <Paragraph type="secondary">
          Monitor performance metrics and track key business indicators.
        </Paragraph>
      </div>

      {/* Metrics Summary */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {metrics.map((metric, i) => (
          <Col xs={12} lg={6} key={i}>
            <Card style={{ borderRadius: 12, textAlign: 'center' }}>
              <Text type="secondary" style={{ fontSize: 13 }}>{metric.label}</Text>
              <Title level={2} style={{ margin: '8px 0' }}>{metric.value}</Title>
              <Text style={{ color: metric.up ? '#52c41a' : '#ff4d4f' }}>
                {metric.up ? <RiseOutlined /> : <FallOutlined />} {metric.change}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card
            title="Performance Metrics"
            style={{ borderRadius: 12 }}
            extra={
              <Space>
                <Tag color="blue">Actual</Tag>
                <Tag color="default">Target</Tag>
              </Space>
            }
          >
            <div style={{ height: 280, padding: '20px 10px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 24, height: '100%' }}>
                {chartData.map((item, i) => (
                  <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: 4, justifyContent: 'center', alignItems: 'flex-end', height: 200 }}>
                      <Tooltip title={`Actual: ${item.value}`}>
                        <div style={{
                          width: 30,
                          height: `${item.value * 2}px`,
                          background: 'linear-gradient(180deg, #1890ff 0%, #69c0ff 100%)',
                          borderRadius: '6px 6px 0 0',
                          cursor: 'pointer',
                          transition: 'transform 0.2s'
                        }} />
                      </Tooltip>
                      <Tooltip title={`Target: ${item.target}`}>
                        <div style={{
                          width: 20,
                          height: `${item.target * 2}px`,
                          background: '#f0f0f0',
                          borderRadius: '6px 6px 0 0',
                          cursor: 'pointer',
                          border: '2px dashed #d9d9d9'
                        }} />
                      </Tooltip>
                    </div>
                    <Text type="secondary" style={{ fontSize: 13, marginTop: 8, display: 'block' }}>
                      {item.month}
                    </Text>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="System Health" style={{ borderRadius: 12 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Server Uptime</Text>
                  <Text strong style={{ color: '#52c41a' }}>99.9%</Text>
                </Space>
                <Progress percent={99.9} size="small" showInfo={false} strokeColor="#52c41a" />
              </div>
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Response Time</Text>
                  <Text strong style={{ color: '#1890ff' }}>45ms</Text>
                </Space>
                <Progress percent={85} size="small" showInfo={false} strokeColor="#1890ff" />
              </div>
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Error Rate</Text>
                  <Text strong style={{ color: '#52c41a' }}>0.1%</Text>
                </Space>
                <Progress percent={2} size="small" showInfo={false} strokeColor="#52c41a" />
              </div>
              <div>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Text>Memory Usage</Text>
                  <Text strong style={{ color: '#faad14' }}>67%</Text>
                </Space>
                <Progress percent={67} size="small" showInfo={false} strokeColor="#faad14" />
              </div>
            </Space>
          </Card>

          <Card title="Top Pages" style={{ borderRadius: 12, marginTop: 16 }}>
            <List
              size="small"
              dataSource={[
                { page: '/dashboard', views: '12,456' },
                { page: '/products', views: '8,234' },
                { page: '/checkout', views: '5,678' },
                { page: '/profile', views: '3,421' },
              ]}
              renderItem={item => (
                <List.Item style={{ padding: '8px 0' }}>
                  <Text code>{item.page}</Text>
                  <Tag color="blue">{item.views} views</Tag>
                </List.Item>
              )}
            />
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
  const [collapsed, setCollapsed] = useState(false);

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
      <Sider
        width={240}
        theme="light"
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
          zIndex: 10
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
          marginBottom: 8
        }}>
          <Title level={4} style={{ margin: 0, color: '#fff' }}>
            {collapsed ? 'WB' : 'Work Buddy'}
          </Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0, marginTop: 8 }}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          zIndex: 9
        }}>
          <Space>
            <HomeOutlined style={{ color: '#1890ff', fontSize: 18 }} />
            <Text strong style={{ fontSize: 16 }}>Enterprise Portal</Text>
          </Space>
          <Space size="large">
            <Tooltip title="Notifications">
              <Badge count={5} size="small">
                <BellOutlined style={{ fontSize: 18, cursor: 'pointer', color: '#666' }} />
              </Badge>
            </Tooltip>
            <Divider type="vertical" />
            <Space>
              <Avatar style={{ backgroundColor: '#1890ff' }} icon={<UserOutlined />} />
              <Text>{user?.name}</Text>
              <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout} danger>
                Logout
              </Button>
            </Space>
          </Space>
        </Header>
        <Content style={{
          margin: 24,
          padding: 24,
          background: '#fff',
          borderRadius: 12,
          minHeight: 280,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
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
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 8,
          },
        }}
      >
        <div style={{ padding: 24, minHeight: '100vh', background: '#f5f5f5' }}>
          <Card style={{ maxWidth: 800, margin: '0 auto', borderRadius: 12 }}>
            <Title level={3}>Mock {toolId.toUpperCase()} Service</Title>
            <Paragraph>This is a mock UI for {toolId}. For full testing, use the React App mode.</Paragraph>
            <Form>
              <Form.Item label="Search">
                <Input.Search placeholder={`Search in ${toolId}...`} size="large" />
              </Form.Item>
            </Form>
            <Button type="primary" size="large">Mock Action</Button>
          </Card>
        </div>
      </ConfigProvider>
    );
  }

  // Full React App with Ant Design for testing
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          colorSuccess: '#52c41a',
          colorWarning: '#faad14',
          colorError: '#ff4d4f',
          colorInfo: '#1890ff',
          borderRadius: 8,
          fontSize: 14,
        },
        components: {
          Card: {
            borderRadiusLG: 12,
          },
          Button: {
            borderRadius: 6,
          },
          Input: {
            borderRadius: 6,
          },
        },
      }}
    >
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
    </ConfigProvider>
  );
}

export default App;