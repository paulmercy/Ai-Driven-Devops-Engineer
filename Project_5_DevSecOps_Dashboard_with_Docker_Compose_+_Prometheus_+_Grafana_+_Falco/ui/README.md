# DevSecOps Dashboard UI

A modern, responsive web interface for monitoring and managing your DevSecOps stack.

## 🎯 Features

### 📊 **Overview Dashboard**
- Real-time system health monitoring
- Key performance metrics
- Service status indicators
- Quick action buttons

### 🛡️ **Security Monitoring**
- Security status overview
- Threat detection metrics
- Real-time security alerts
- Falco integration status

### 📈 **Monitoring & Metrics**
- Embedded Grafana dashboards
- Prometheus target status
- System resource monitoring
- Performance metrics visualization

### ⚙️ **Service Management**
- Service control panel
- Individual service management
- Real-time status monitoring
- Log viewing capabilities

### 🐛 **Attack Simulation**
- Security testing tools
- Multiple attack scenarios
- Real-time results logging
- Alert trigger testing

### 📝 **System Logs**
- Centralized log viewing
- Log level filtering
- Real-time log streaming
- Search and filter capabilities

## 🚀 Quick Start

### 1. Access the Dashboard

Once your DevSecOps stack is running, access the dashboard at:

```
http://localhost:3000/dashboard
```

### 2. Navigation

Use the top navigation bar to switch between sections:
- **Overview**: System status and quick actions
- **Security**: Security monitoring and alerts
- **Monitoring**: Metrics and performance data
- **Services**: Service management and control
- **Attack Sim**: Security testing tools
- **Logs**: System logs and events

### 3. Quick Actions

From the Overview section, you can:
- Open Grafana dashboard
- Open Prometheus interface
- Run health checks
- Simulate security attacks

## 🎨 UI Components

### Status Indicators
- 🟢 **Green**: Healthy/Active
- 🟡 **Yellow**: Warning/Degraded
- 🔴 **Red**: Error/Inactive

### Metrics Cards
Real-time display of:
- System health status
- Security alert counts
- Active connections
- Response times

### Service Cards
Individual service monitoring with:
- Health status indicators
- Port information
- Quick action buttons

## 🔧 Configuration

### API Endpoints
The dashboard connects to these endpoints:
- `http://localhost:3000` - Demo Application
- `http://localhost:9090` - Prometheus
- `http://localhost:3001` - Grafana

### Refresh Settings
- Auto-refresh: Every 30 seconds
- Manual refresh: Click refresh buttons
- Real-time updates: WebSocket connections (future)

## 🎯 Keyboard Shortcuts

- `Ctrl/Cmd + R`: Refresh dashboard
- `Ctrl/Cmd + 1`: Switch to Overview
- `Ctrl/Cmd + 2`: Switch to Security

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

## 🛠️ Technical Details

### Technologies Used
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Modern CSS with Flexbox/Grid
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)

### Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Performance
- Lightweight: < 500KB total
- Fast loading: < 2 seconds
- Efficient updates: Minimal DOM manipulation

## 🔍 Troubleshooting

### Dashboard Not Loading
1. Check if the demo app is running on port 3000
2. Verify CORS settings allow browser access
3. Check browser console for errors

### Services Showing as Unhealthy
1. Verify all containers are running: `docker-compose ps`
2. Check service logs: `docker-compose logs [service-name]`
3. Test individual endpoints manually

### Metrics Not Updating
1. Check Prometheus is scraping targets
2. Verify network connectivity between services
3. Check for firewall or port blocking issues

## 🚀 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Custom dashboard layouts
- [ ] Dark/light theme toggle
- [ ] Export capabilities
- [ ] Mobile app version
- [ ] Multi-language support

## 📄 License

This UI is part of the DevSecOps Dashboard project and follows the same licensing terms.

---

**Happy Monitoring! 🛡️📊**
