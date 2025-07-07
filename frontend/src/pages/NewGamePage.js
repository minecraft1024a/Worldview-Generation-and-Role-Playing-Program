import React, { useState } from 'react';
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
  CardActions,
  CircularProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Divider
} from '@mui/material';
import {
  ArrowBack,
  PlayArrow,
  Refresh,
  Edit,
  Check
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import ReactMarkdown from 'react-markdown';

const NewGamePage = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [background, setBackground] = useState('');
  const [worldDescription, setWorldDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const steps = ['设定世界观背景', '生成世界观', '确认并开始游戏'];

  const handleBackgroundSubmit = async () => {
    if (!background.trim()) {
      setBackground('地理、历史、文化、魔法体系');
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await apiService.generateWorld(background || '地理、历史、文化、魔法体系');
      if (response.success) {
        setWorldDescription(response.world_description);
        setActiveStep(1);
      } else {
        setError(response.message || '世界观生成失败');
      }
    } catch (err) {
      setError('生成世界观时发生错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setActiveStep(0);
    setWorldDescription('');
  };

  const handleEditBackground = () => {
    setActiveStep(0);
  };

  const handleStartGame = () => {
    // 导航到游戏页面，传递世界观数据
    navigate('/game', { 
      state: { 
        worldDescription,
        isNewGame: true
      }
    });
  };

  const handleBack = () => {
    navigate('/');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* 页面标题 */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <Button
            startIcon={<ArrowBack />}
            onClick={handleBack}
            sx={{ mr: 2 }}
          >
            返回主菜单
          </Button>
          <Typography variant="h4" component="h1" color="primary">
            🌍 新游戏创建
          </Typography>
        </Box>
        
        {/* 步骤指示器 */}
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mt: 3 }}>
          {steps.map((label, index) => (
            <Step key={label} completed={activeStep > index}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* 步骤 1: 输入背景 */}
      {activeStep === 0 && (
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom>
              📝 描述您想要的世界观背景
            </Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              例如：魔法学院、赛博朋克、古代仙侠、科幻太空等。留空将使用默认设定。
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="描述您想要的世界观背景设定..."
              variant="outlined"
              sx={{ mt: 2, mb: 3 }}
            />
            <Typography variant="body2" color="text.secondary" gutterBottom>
              提示：越详细的描述将生成更符合您期望的世界观
            </Typography>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              color="primary"
              onClick={handleBackgroundSubmit}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              size="large"
            >
              {loading ? '正在生成世界观...' : '生成世界观'}
            </Button>
          </CardActions>
        </Card>
      )}

      {/* 步骤 2: 显示生成的世界观 */}
      {activeStep === 1 && worldDescription && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom color="primary">
                  🌍 生成的世界观
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Paper
                  elevation={1}
                  sx={{
                    p: 3,
                    maxHeight: '400px',
                    overflow: 'auto',
                    backgroundColor: '#f5f5f5'
                  }}
                >
                  <ReactMarkdown>{worldDescription}</ReactMarkdown>
                </Paper>
              </CardContent>
              <CardActions sx={{ justifyContent: 'space-between', p: 3 }}>
                <Box>
                  <Button
                    variant="outlined"
                    startIcon={<Edit />}
                    onClick={handleEditBackground}
                    sx={{ mr: 2 }}
                  >
                    修改背景设定
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={handleRegenerate}
                    disabled={loading}
                  >
                    重新生成世界观
                  </Button>
                </Box>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  startIcon={<Check />}
                  onClick={() => setActiveStep(2)}
                >
                  接受此世界观
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 步骤 3: 确认开始游戏 */}
      {activeStep === 2 && (
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom color="primary">
              🎮 准备开始游戏
            </Typography>
            <Typography variant="body1" gutterBottom>
              世界观已确认！现在您可以开始您的冒险之旅了。
            </Typography>
            <Box sx={{ mt: 3, p: 2, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>提示：</strong>游戏开始后，您可以随时保存进度，也可以通过输入指令来与游戏世界互动。
              </Typography>
            </Box>
          </CardContent>
          <CardActions>
            <Button
              variant="outlined"
              onClick={() => setActiveStep(1)}
              sx={{ mr: 2 }}
            >
              返回修改
            </Button>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleStartGame}
            >
              开始游戏
            </Button>
          </CardActions>
        </Card>
      )}

      {loading && activeStep === 0 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress size={60} />
        </Box>
      )}
    </Container>
  );
};

export default NewGamePage;
