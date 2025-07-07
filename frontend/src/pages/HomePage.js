import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  PlayArrow,
  FolderOpen,
  Info,
  FormatQuote
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const HomePage = () => {
  const navigate = useNavigate();
  const [dailyQuote, setDailyQuote] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDailyQuote = async () => {
      try {
        const response = await apiService.getDailyQuote();
        if (response.success) {
          setDailyQuote(response.quote);
        } else {
          setDailyQuote('欢迎来到WGARP世界！');
        }
      } catch (err) {
        console.error('Failed to fetch daily quote:', err);
        setDailyQuote('欢迎来到WGARP世界！');
      } finally {
        setLoading(false);
      }
    };

    fetchDailyQuote();
  }, []);

  const handleNewGame = () => {
    navigate('/new-game');
  };

  const handleLoadGame = () => {
    navigate('/load-game');
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* 标题横幅 */}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          mb: 4,
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          WGARP
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom>
          世界观生成与角色扮演程序
        </Typography>
        <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
          开启你的冒险之旅
        </Typography>
      </Paper>

      <Grid container spacing={4}>
        {/* 主菜单 */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h5" component="h3" gutterBottom color="primary">
                🎮 主菜单
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    size="large"
                    startIcon={<PlayArrow />}
                    onClick={handleNewGame}
                    sx={{ py: 2 }}
                  >
                    🌟 开始新游戏
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    color="primary"
                    fullWidth
                    size="large"
                    startIcon={<FolderOpen />}
                    onClick={handleLoadGame}
                    sx={{ py: 2 }}
                  >
                    📖 读取存档开始游戏
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 程序信息 */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom color="secondary">
                程序信息
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" color="primary" gutterBottom>
                  WGARP
                </Typography>
                <Chip label="Version 2.1-alpha(web)" size="small" color="secondary" sx={{ mb: 1 }} />
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  作者: xxx
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  QQ群: 123456
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  开源协议: GPL3
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 每日一言 */}
        <Grid item xs={12}>
          <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <FormatQuote sx={{ color: 'white', mr: 1 }} />
                <Typography variant="h6" color="white">
                  💡 每日一言
                </Typography>
              </Box>
              <Typography variant="body1" color="white" sx={{ fontStyle: 'italic', fontSize: '1.1rem' }}>
                {dailyQuote}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 功能介绍 */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                <Info sx={{ mr: 1, verticalAlign: 'middle' }} />
                功能介绍
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h4" gutterBottom>🌍</Typography>
                    <Typography variant="subtitle1" gutterBottom>智能世界观生成</Typography>
                    <Typography variant="body2" color="text.secondary">
                      AI 驱动的世界构建，创造独特的冒险背景
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h4" gutterBottom>🎭</Typography>
                    <Typography variant="subtitle1" gutterBottom>角色扮演互动</Typography>
                    <Typography variant="body2" color="text.secondary">
                      沉浸式的角色扮演体验，与 AI 进行深度互动
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h4" gutterBottom>💾</Typography>
                    <Typography variant="subtitle1" gutterBottom>智能存档系统</Typography>
                    <Typography variant="body2" color="text.secondary">
                      自动生成摘要，智能管理游戏进度
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h4" gutterBottom>🎨</Typography>
                    <Typography variant="subtitle1" gutterBottom>现代化界面</Typography>
                    <Typography variant="body2" color="text.secondary">
                      美观直观的 Web 界面，优秀的用户体验
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage;
