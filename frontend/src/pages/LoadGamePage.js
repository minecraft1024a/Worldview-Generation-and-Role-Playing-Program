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
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip
} from '@mui/material';
import {
  ArrowBack,
  PlayArrow,
  Delete,
  Refresh,
  FolderOpen,
  Schedule,
  Description
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const LoadGamePage = () => {
  const navigate = useNavigate();
  const [saves, setSaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingGame, setLoadingGame] = useState(false);
  const [error, setError] = useState('');
  const [deleteDialog, setDeleteDialog] = useState({ open: false, saveName: '', fileName: '' });

  useEffect(() => {
    fetchSaves();
  }, []);

  const fetchSaves = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await apiService.getSaves();
      if (response.success) {
        setSaves(response.saves);
      } else {
        setError(response.message || '获取存档列表失败');
      }
    } catch (err) {
      setError('获取存档列表时发生错误');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadGame = async (saveName) => {
    setLoadingGame(true);
    setError('');
    
    try {
      const response = await apiService.loadGame(saveName);
      if (response.success) {
        // 导航到游戏页面，传递加载的游戏数据
        navigate('/game', {
          state: {
            worldDescription: response.world_description,
            summary: response.summary,
            saveName: response.save_name,
            lastConversation: response.last_conversation,
            role: response.role,
            isNewGame: false
          }
        });
      } else {
        setError(response.message || '加载游戏失败');
      }
    } catch (err) {
      setError('加载游戏时发生错误');
    } finally {
      setLoadingGame(false);
    }
  };

  const handleDeleteSave = async () => {
    try {
      const response = await apiService.deleteSave(deleteDialog.saveName);
      if (response.success) {
        setSaves(saves.filter(save => save.filename !== deleteDialog.saveName));
        setDeleteDialog({ open: false, saveName: '', fileName: '' });
      } else {
        setError(response.message || '删除存档失败');
      }
    } catch (err) {
      setError('删除存档时发生错误');
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  const formatTime = (timeStr) => {
    if (timeStr === '未知') return '未知时间';
    try {
      const date = new Date(timeStr);
      return date.toLocaleString('zh-CN');
    } catch {
      return timeStr;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* 页面标题 */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <Button
              startIcon={<ArrowBack />}
              onClick={handleBack}
              sx={{ mr: 2 }}
            >
              返回主菜单
            </Button>
            <Typography variant="h4" component="h1" color="primary">
              📚 读取存档
            </Typography>
          </Box>
          <Button
            startIcon={<Refresh />}
            onClick={fetchSaves}
            disabled={loading}
            variant="outlined"
          >
            刷新列表
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress size={60} />
        </Box>
      ) : saves.length === 0 ? (
        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <FolderOpen sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary" gutterBottom>
              暂无存档
            </Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              您还没有保存过任何游戏进度
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/new-game')}
              sx={{ mt: 2 }}
            >
              开始新游戏
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h5" component="h2" gutterBottom>
                  📄 可用存档列表 ({saves.length} 个)
                </Typography>
                <List>
                  {saves.map((save, index) => (
                    <React.Fragment key={save.filename}>
                      <ListItem
                        sx={{
                          border: '1px solid #e0e0e0',
                          borderRadius: 1,
                          mb: 1,
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center">
                              <Typography variant="h6" component="span">
                                {save.filename}
                              </Typography>
                              <Chip
                                label={`存档 ${index + 1}`}
                                size="small"
                                color="primary"
                                sx={{ ml: 2 }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box mt={1}>
                              <Box display="flex" alignItems="center" mb={1}>
                                <Schedule sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                <Typography variant="body2" color="text.secondary">
                                  {formatTime(save.last_updated)}
                                </Typography>
                              </Box>
                              <Box display="flex" alignItems="flex-start">
                                <Description sx={{ fontSize: 16, mr: 1, color: 'text.secondary', mt: 0.2 }} />
                                <Typography variant="body2" color="text.secondary">
                                  {save.summary_preview}
                                </Typography>
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box>
                            <Button
                              variant="contained"
                              color="primary"
                              startIcon={<PlayArrow />}
                              onClick={() => handleLoadGame(save.filename)}
                              disabled={loadingGame}
                              sx={{ mr: 1 }}
                            >
                              {loadingGame ? <CircularProgress size={20} /> : '加载游戏'}
                            </Button>
                            <IconButton
                              edge="end"
                              color="error"
                              onClick={() => setDeleteDialog({
                                open: true,
                                saveName: save.filename,
                                fileName: save.filename
                              })}
                            >
                              <Delete />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 删除确认对话框 */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, saveName: '', fileName: '' })}
      >
        <DialogTitle>确认删除存档</DialogTitle>
        <DialogContent>
          <DialogContentText>
            您确定要删除存档 "{deleteDialog.fileName}" 吗？此操作无法撤销。
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialog({ open: false, saveName: '', fileName: '' })}
          >
            取消
          </Button>
          <Button
            onClick={handleDeleteSave}
            color="error"
            variant="contained"
          >
            删除
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LoadGamePage;
