import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Send,
  Save,
  ExitToApp,
  Person,
  Public,
  History,
  Settings
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import { apiService } from '../services/api';
import ReactMarkdown from 'react-markdown';

const GamePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const {
    isConnected,
    error: wsError,
    connect,
    disconnect,
    sendMessage,
    addMessageListener
  } = useWebSocket();

  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [gameSession, setGameSession] = useState(null);
  const [exitDialog, setExitDialog] = useState(false);
  const messagesEndRef = useRef(null);

  // 从路由状态获取游戏数据
  const gameData = location.state || {};

  useEffect(() => {
    // 连接WebSocket
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  useEffect(() => {
    // 滚动到底部
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isConnected && gameData) {
      initializeGame();
    }
  }, [isConnected, gameData]);

  useEffect(() => {
    // 添加WebSocket事件监听器
    const listeners = [
      addMessageListener('game_started', handleGameStarted),
      addMessageListener('game_loaded', handleGameLoaded),
      addMessageListener('ai_response', handleAiResponse),
      addMessageListener('game_saved', handleGameSaved),
      addMessageListener('error', handleWsError)
    ];

    return () => {
      listeners.forEach(cleanup => cleanup());
    };
  }, [addMessageListener]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeGame = async () => {
    try {
      if (gameData.isNewGame) {
        // 新游戏
        sendMessage('start_game', {
          world_description: gameData.worldDescription,
          save_name: null
        });
      } else {
        // 加载游戏
        sendMessage('load_game', {
          save_name: gameData.saveName
        });
      }
    } catch (err) {
      setError('初始化游戏失败');
    }
  };

  const handleGameStarted = (data) => {
    setGameSession({
      sessionId: data.session_id,
      worldDescription: data.world_description,
      saveName: null
    });
    
    // 添加系统消息
    addMessage('system', `🌍 欢迎来到新的世界！\n\n${data.world_description}\n\n✨ 您的冒险即将开始...`);
  };

  const handleGameLoaded = (data) => {
    setGameSession({
      sessionId: data.session_id,
      worldDescription: data.world_description,
      saveName: data.save_name || gameData.saveName
    });

    // 添加系统消息
    addMessage('system', `📚 存档已加载: ${gameData.saveName}\n\n🌍 世界观：\n${data.world_description}\n\n📖 游戏摘要：\n${data.summary}`);
    
    // 如果有最后的对话，添加到消息列表
    if (data.last_conversation) {
      addMessage(data.last_conversation.role, data.last_conversation.content);
    }
  };

  const handleAiResponse = (data) => {
    addMessage('assistant', data.content);
    setLoading(false);
  };

  const handleGameSaved = (data) => {
    setSaving(false);
    setGameSession(prev => ({
      ...prev,
      saveName: data.save_name
    }));
    addMessage('system', `💾 游戏已保存: ${data.save_name}`);
  };

  const handleWsError = (data) => {
    setError(data.message);
    setLoading(false);
    setSaving(false);
  };

  const addMessage = (role, content) => {
    const newMessage = {
      role,
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = () => {
    if (!inputText.trim() || loading || !isConnected) return;

    const userMessage = inputText.trim();
    addMessage('user', userMessage);
    setInputText('');
    setLoading(true);

    try {
      sendMessage('player_action', {
        content: userMessage
      });
    } catch (err) {
      setError('发送消息失败');
      setLoading(false);
    }
  };

  const handleSaveGame = () => {
    if (!isConnected || saving) return;

    setSaving(true);
    try {
      sendMessage('save_game');
    } catch (err) {
      setError('保存游戏失败');
      setSaving(false);
    }
  };

  const handleExitGame = () => {
    setExitDialog(true);
  };

  const confirmExit = () => {
    disconnect();
    navigate('/');
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageColor = (role) => {
    switch (role) {
      case 'user':
        return '#e3f2fd';
      case 'assistant':
        return '#f3e5f5';
      case 'system':
        return '#e8f5e8';
      default:
        return '#f5f5f5';
    }
  };

  const getMessageIcon = (role) => {
    switch (role) {
      case 'user':
        return '👤';
      case 'assistant':
        return '🎭';
      case 'system':
        return '⚙️';
      default:
        return '💬';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isConnected) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          正在连接游戏服务器...
        </Typography>
        {wsError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            连接失败: {wsError}
          </Alert>
        )}
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 2, height: 'calc(100vh - 100px)' }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* 侧边栏 */}
        <Grid item xs={12} md={3}>
          <Grid container spacing={2} sx={{ height: '100%' }}>
            {/* 游戏信息 */}
            <Grid item xs={12}>
              <Card sx={{ height: 'fit-content' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    <Public sx={{ mr: 1, verticalAlign: 'middle' }} />
                    游戏信息
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={gameSession?.saveName || '新游戏'}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    连接状态: {isConnected ? '🟢 已连接' : '🔴 未连接'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* 操作按钮 */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    <Settings sx={{ mr: 1, verticalAlign: 'middle' }} />
                    游戏操作
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<Save />}
                      onClick={handleSaveGame}
                      disabled={saving || !isConnected}
                      fullWidth
                    >
                      {saving ? <CircularProgress size={20} /> : '保存游戏'}
                    </Button>
                    <Button
                      variant="outlined"
                      color="secondary"
                      startIcon={<ExitToApp />}
                      onClick={handleExitGame}
                      fullWidth
                    >
                      退出游戏
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* 主游戏区域 */}
        <Grid item xs={12} md={9}>
          <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* 消息区域 */}
            <Box
              sx={{
                flex: 1,
                overflow: 'auto',
                p: 2,
                backgroundColor: '#fafafa'
              }}
            >
              <List>
                {messages.map((message, index) => (
                  <ListItem key={index} sx={{ mb: 1 }}>
                    <Card
                      sx={{
                        width: '100%',
                        backgroundColor: getMessageColor(message.role),
                        maxWidth: message.role === 'user' ? '80%' : '100%',
                        ml: message.role === 'user' ? 'auto' : 0
                      }}
                    >
                      <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                        <Box display="flex" alignItems="center" mb={1}>
                          <Typography variant="body2" sx={{ mr: 1 }}>
                            {getMessageIcon(message.role)}
                          </Typography>
                          <Typography variant="subtitle2" color="primary">
                            {message.role === 'user' ? '玩家' : 
                             message.role === 'assistant' ? 'AI' : '系统'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                            {formatTimestamp(message.timestamp)}
                          </Typography>
                        </Box>
                        <Box sx={{ '& p': { mb: 1 }, '& p:last-child': { mb: 0 } }}>
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </Box>
                      </CardContent>
                    </Card>
                  </ListItem>
                ))}
                {loading && (
                  <ListItem>
                    <Box display="flex" alignItems="center">
                      <CircularProgress size={20} sx={{ mr: 2 }} />
                      <Typography variant="body2" color="text.secondary">
                        AI 正在思考...
                      </Typography>
                    </Box>
                  </ListItem>
                )}
              </List>
              <div ref={messagesEndRef} />
            </Box>

            <Divider />

            {/* 输入区域 */}
            <Box sx={{ p: 2 }}>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入您的行动或对话..."
                  variant="outlined"
                  disabled={loading || !isConnected}
                />
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={!inputText.trim() || loading || !isConnected}
                  sx={{ minWidth: '80px' }}
                >
                  <Send />
                </Button>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                按 Enter 发送，Shift + Enter 换行
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* 退出确认对话框 */}
      <Dialog open={exitDialog} onClose={() => setExitDialog(false)}>
        <DialogTitle>确认退出游戏</DialogTitle>
        <DialogContent>
          <Typography>
            您确定要退出游戏吗？建议先保存游戏进度。
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExitDialog(false)}>
            取消
          </Button>
          <Button onClick={handleSaveGame} color="primary" disabled={saving}>
            保存并退出
          </Button>
          <Button onClick={confirmExit} color="error">
            直接退出
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default GamePage;
