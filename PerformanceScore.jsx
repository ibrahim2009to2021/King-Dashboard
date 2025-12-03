import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Star,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

const PerformanceScore = ({ 
  score = 75, 
  metric = "Overall Performance", 
  benchmark = 65,
  trend = "up",
  trendValue = 12.5,
  size = "medium" 
}) => {
  const theme = useTheme();

  // Determine score color and status
  const getScoreStatus = (score) => {
    if (score >= 85) return { label: 'Excellent', color: 'success', icon: <Star /> };
    if (score >= 70) return { label: 'Good', color: 'primary', icon: <CheckCircle /> };
    if (score >= 50) return { label: 'Average', color: 'warning', icon: <Warning /> };
    return { label: 'Needs Improvement', color: 'error', icon: <Warning /> };
  };

  // Get trend icon and color
  const getTrendIndicator = (trend) => {
    switch (trend) {
      case 'up':
        return { icon: <TrendingUp />, color: 'success.main', sign: '+' };
      case 'down':
        return { icon: <TrendingDown />, color: 'error.main', sign: '' };
      default:
        return { icon: <TrendingFlat />, color: 'text.secondary', sign: '' };
    }
  };

  const status = getScoreStatus(score);
  const trendIndicator = getTrendIndicator(trend);
  const isAboveBenchmark = score > benchmark;

  // Size variants
  const sizeConfig = {
    small: {
      cardPadding: 2,
      scoreSize: '2rem',
      titleSize: 'body2',
      showDetails: false
    },
    medium: {
      cardPadding: 3,
      scoreSize: '2.5rem',
      titleSize: 'h6',
      showDetails: true
    },
    large: {
      cardPadding: 4,
      scoreSize: '3rem',
      titleSize: 'h5',
      showDetails: true
    }
  };

  const config = sizeConfig[size] || sizeConfig.medium;

  return (
    <Card 
      sx={{ 
        height: '100%',
        position: 'relative',
        background: `linear-gradient(135deg, 
          ${theme.palette.background.paper} 0%, 
          ${theme.palette.background.default} 100%)`,
        border: `1px solid ${theme.palette.divider}`,
        '&:hover': {
          boxShadow: theme.shadows[4],
          transform: 'translateY(-2px)',
          transition: 'all 0.3s ease',
        }
      }}
    >
      <CardContent sx={{ p: config.cardPadding }}>
        {/* Header with metric name and status */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant={config.titleSize} component="h3" sx={{ fontWeight: 600 }}>
            {metric}
          </Typography>
          
          <Chip
            icon={status.icon}
            label={status.label}
            color={status.color}
            size="small"
            sx={{ minWidth: 'auto' }}
          />
        </Box>

        {/* Score Display */}
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography 
            variant="h2" 
            component="div" 
            sx={{ 
              fontWeight: 700,
              fontSize: config.scoreSize,
              color: `${status.color}.main`,
              lineHeight: 1
            }}
          >
            {score}
            <Typography 
              component="span" 
              variant="h5" 
              sx={{ color: 'text.secondary', ml: 0.5 }}
            >
              /100
            </Typography>
          </Typography>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: 2 }}>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                backgroundColor: `${status.color}.main`,
              },
            }}
          />
          
          {/* Benchmark indicator */}
          {config.showDetails && (
            <Box sx={{ position: 'relative', mt: 1 }}>
              <Box
                sx={{
                  position: 'absolute',
                  left: `${benchmark}%`,
                  transform: 'translateX(-50%)',
                  textAlign: 'center',
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  Industry: {benchmark}
                </Typography>
                <Box
                  sx={{
                    width: 2,
                    height: 12,
                    backgroundColor: 'text.secondary',
                    margin: '0 auto',
                  }}
                />
              </Box>
            </Box>
          )}
        </Box>

        {/* Details */}
        {config.showDetails && (
          <Box>
            {/* Trend Information */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ color: trendIndicator.color, display: 'flex', alignItems: 'center' }}>
                  {trendIndicator.icon}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {trendIndicator.sign}{trendValue}% vs last period
                </Typography>
              </Box>
            </Box>

            {/* Benchmark Comparison */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                vs Industry Benchmark:
              </Typography>
              <Chip
                label={`${isAboveBenchmark ? '+' : ''}${(score - benchmark).toFixed(1)}`}
                size="small"
                color={isAboveBenchmark ? 'success' : 'error'}
                sx={{ minWidth: 'auto' }}
              />
            </Box>
          </Box>
        )}
      </CardContent>

      {/* Performance indicator badge */}
      {score >= 90 && (
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            width: 20,
            height: 20,
            borderRadius: '50%',
            backgroundColor: 'success.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'success.contrastText',
          }}
        >
          <Star sx={{ fontSize: 12 }} />
        </Box>
      )}
    </Card>
  );
};

// Variant for compact display in lists
export const CompactPerformanceScore = ({ score, metric, trend, trendValue }) => {
  const status = score >= 70 ? 'success' : score >= 50 ? 'warning' : 'error';
  const trendColor = trend === 'up' ? 'success.main' : trend === 'down' ? 'error.main' : 'text.secondary';
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 1 }}>
      <Box sx={{ minWidth: 120 }}>
        <Typography variant="body2" fontWeight="medium">
          {metric}
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 80 }}>
        <Typography variant="h6" color={`${status}.main`} fontWeight="bold">
          {score}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          /100
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: trendColor }}>
        {trend === 'up' ? <TrendingUp fontSize="small" /> : 
         trend === 'down' ? <TrendingDown fontSize="small" /> : 
         <TrendingFlat fontSize="small" />}
        <Typography variant="caption" fontWeight="medium">
          {trend === 'up' ? '+' : ''}{trendValue}%
        </Typography>
      </Box>
    </Box>
  );
};

export default PerformanceScore;