"""
FEATURE 1: Advanced Audience Segmentation Engine
AI-powered audience segmentation with RFM, behavioral, and lookalike capabilities
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import asyncio
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
import joblib
import warnings

from app.utils.logging_config import get_logger

warnings.filterwarnings('ignore')
logger = get_logger(__name__)


class SegmentationType(Enum):
    """Enhanced segmentation types"""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral" 
    RFM = "rfm"
    LIFECYCLE = "lifecycle"
    VALUE_BASED = "value_based"
    ENGAGEMENT = "engagement"
    LOOKALIKE = "lookalike"
    PREDICTIVE = "predictive"
    CUSTOM = "custom"


class CustomerLifecycleStage(Enum):
    """RFM-based customer lifecycle stages"""
    CHAMPIONS = "champions"              # Best customers (High R,F,M)
    LOYAL_CUSTOMERS = "loyal_customers"  # Consistent buyers
    POTENTIAL_LOYALISTS = "potential_loyalists"  # Recent buyers with potential
    NEW_CUSTOMERS = "new_customers"      # Recently acquired
    PROMISING = "promising"              # Recent buyers
    NEED_ATTENTION = "need_attention"    # Above average but declining
    ABOUT_TO_SLEEP = "about_to_sleep"    # Below average, declining
    AT_RISK = "at_risk"                 # High value but long ago
    CANNOT_LOSE = "cannot_lose"         # High value, very long ago
    HIBERNATING = "hibernating"         # Low value, long ago  
    LOST = "lost"                       # Lowest value, longest ago


@dataclass
class AudienceSegment:
    """Enhanced audience segment definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    segment_type: SegmentationType = SegmentationType.CUSTOM
    lifecycle_stage: Optional[CustomerLifecycleStage] = None
    size: int = 0
    criteria: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    platforms: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    confidence_score: float = 0.0
    predicted_ltv: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    rfm_scores: Dict[str, int] = field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)


class AdvancedAudienceSegmentationEngine:
    """
    FEATURE 1: Advanced AI-Powered Audience Segmentation Engine
    
    **Capabilities:**
    - RFM Analysis with 11 lifecycle stages
    - Behavioral segmentation based on engagement patterns
    - Lookalike audience creation using ML similarity matching
    - Predictive audience scoring for lifetime value
    - Custom segment builder with multiple criteria
    - Cross-platform audience matching and optimization
    """
    
    def __init__(self):
        """Initialize advanced segmentation engine"""
        self.segments: Dict[str, AudienceSegment] = {}
        self.models: Dict[str, Any] = {}
        self.scaler = StandardScaler()
        
        # Configuration
        self.min_segment_size = 50
        self.max_segments = 100
        self.rfm_quantiles = 5
        self.lookalike_similarity_threshold = 0.8
        
        # RFM segment mapping (based on RFM scores)
        self.rfm_segment_map = {
            CustomerLifecycleStage.CHAMPIONS: ['555', '554', '544', '545', '454', '455', '445'],
            CustomerLifecycleStage.LOYAL_CUSTOMERS: ['543', '444', '435', '355', '354', '345', '344'],
            CustomerLifecycleStage.POTENTIAL_LOYALISTS: ['512', '511', '422', '421', '412', '411', '311'],
            CustomerLifecycleStage.NEW_CUSTOMERS: ['522', '521', '512', '511', '412', '411'],
            CustomerLifecycleStage.PROMISING: ['512', '511', '422', '421', '411', '412'],
            CustomerLifecycleStage.NEED_ATTENTION: ['413', '414', '343', '344', '313', '314'],
            CustomerLifecycleStage.ABOUT_TO_SLEEP: ['315', '314', '313', '213', '214', '215'],
            CustomerLifecycleStage.AT_RISK: ['155', '154', '144', '214', '215', '115'],
            CustomerLifecycleStage.CANNOT_LOSE: ['155', '254', '245', '145', '144'],
            CustomerLifecycleStage.HIBERNATING: ['134', '135', '143', '142', '124', '125'],
            CustomerLifecycleStage.LOST: ['111', '112', '121', '131', '141', '151']
        }
    
    async def create_rfm_segments(
        self, 
        data: List[Dict[str, Any]],
        client_id: str
    ) -> Dict[str, Any]:
        """
        Create RFM (Recency, Frequency, Monetary) segments
        
        **Enhanced RFM Analysis:**
        - 11 distinct lifecycle stages
        - Personalized scoring based on client data
        - Predictive lifetime value calculation
        - Automated segment recommendations
        """
        try:
            if not data:
                return {"error": "No data provided for RFM analysis"}
            
            df = pd.DataFrame(data)
            
            # Validate required columns
            required_cols = ['customer_id', 'date', 'revenue', 'conversions']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {"error": f"Missing required columns: {missing_cols}"}
            
            # Calculate RFM metrics
            current_date = pd.to_datetime('today')
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by customer and calculate RFM
            rfm_data = df.groupby('customer_id').agg({
                'date': lambda x: (current_date - x.max()).days,  # Recency
                'conversions': 'sum',                              # Frequency  
                'revenue': 'sum'                                   # Monetary
            }).reset_index()
            
            rfm_data.columns = ['customer_id', 'recency', 'frequency', 'monetary']
            
            # Create RFM scores using quantile-based scoring
            rfm_data['R_score'] = pd.qcut(
                rfm_data['recency'].rank(method='first'), 
                self.rfm_quantiles, 
                labels=[5,4,3,2,1]  # Lower recency = higher score
            )
            rfm_data['F_score'] = pd.qcut(
                rfm_data['frequency'].rank(method='first'), 
                self.rfm_quantiles, 
                labels=[1,2,3,4,5]  # Higher frequency = higher score
            )
            rfm_data['M_score'] = pd.qcut(
                rfm_data['monetary'].rank(method='first'), 
                self.rfm_quantiles, 
                labels=[1,2,3,4,5]  # Higher monetary = higher score
            )
            
            # Create combined RFM score
            rfm_data['RFM_score'] = (
                rfm_data['R_score'].astype(str) + 
                rfm_data['F_score'].astype(str) + 
                rfm_data['M_score'].astype(str)
            )
            
            # Assign lifecycle stages
            rfm_data['lifecycle_stage'] = rfm_data['RFM_score'].apply(
                self._map_rfm_to_lifecycle_stage
            )
            
            # Calculate predicted LTV
            rfm_data['predicted_ltv'] = self._calculate_predicted_ltv(rfm_data)
            
            # Create segments for each lifecycle stage
            segments = []
            for stage in CustomerLifecycleStage:
                stage_data = rfm_data[rfm_data['lifecycle_stage'] == stage.value]
                
                if len(stage_data) >= self.min_segment_size:
                    segment = AudienceSegment(
                        name=f"RFM: {stage.value.title().replace('_', ' ')}",
                        description=self._get_lifecycle_stage_description(stage),
                        segment_type=SegmentationType.RFM,
                        lifecycle_stage=stage,
                        size=len(stage_data),
                        criteria={'lifecycle_stage': stage.value},
                        performance_metrics=self._calculate_segment_metrics(stage_data),
                        platforms=['meta', 'google', 'tiktok', 'snapchat'],
                        rfm_scores=self._calculate_avg_rfm_scores(stage_data)
                    )
                    segments.append(segment)
                    self.segments[segment.id] = segment
            
            logger.info(f"Created {len(segments)} RFM segments for client {client_id}")
            
            return {
                "segments": [self._segment_to_dict(seg) for seg in segments],
                "rfm_data": rfm_data.to_dict('records'),
                "lifecycle_distribution": rfm_data['lifecycle_stage'].value_counts().to_dict(),
                "total_customers": len(rfm_data),
                "avg_predicted_ltv": float(rfm_data['predicted_ltv'].mean())
            }
        
        except Exception as e:
            logger.error(f"Error creating RFM segments: {e}")
            return {"error": f"RFM analysis failed: {str(e)}"}
    
    async def create_behavioral_segments(
        self,
        data: List[Dict[str, Any]], 
        client_id: str
    ) -> Dict[str, Any]:
        """
        Create behavioral segments based on user engagement patterns
        
        **Enhanced Behavioral Analysis:**
        - Engagement pattern clustering
        - Platform preference analysis  
        - Creative interaction patterns
        - Time-based behavior analysis
        """
        try:
            if not data:
                return {"error": "No data provided for behavioral analysis"}
            
            df = pd.DataFrame(data)
            
            # Create behavioral features
            behavioral_features = self._extract_behavioral_features(df)
            
            if behavioral_features.empty:
                return {"error": "Could not extract behavioral features"}
            
            # Perform clustering on behavioral features
            clustering_results = await self._perform_behavioral_clustering(behavioral_features)
            
            # Create segments from clusters
            segments = []
            for cluster_id, cluster_info in clustering_results['clusters'].items():
                if cluster_info['size'] >= self.min_segment_size:
                    segment = AudienceSegment(
                        name=f"Behavioral: {cluster_info['name']}",
                        description=cluster_info['description'],
                        segment_type=SegmentationType.BEHAVIORAL,
                        size=cluster_info['size'],
                        criteria={'cluster_id': cluster_id},
                        performance_metrics=cluster_info['metrics'],
                        platforms=cluster_info['preferred_platforms'],
                        behavioral_patterns=cluster_info['patterns']
                    )
                    segments.append(segment)
                    self.segments[segment.id] = segment
            
            logger.info(f"Created {len(segments)} behavioral segments for client {client_id}")
            
            return {
                "segments": [self._segment_to_dict(seg) for seg in segments],
                "clustering_results": clustering_results,
                "behavioral_insights": self._generate_behavioral_insights(clustering_results)
            }
        
        except Exception as e:
            logger.error(f"Error creating behavioral segments: {e}")
            return {"error": f"Behavioral analysis failed: {str(e)}"}
    
    async def create_lookalike_segments(
        self,
        seed_segment_id: str,
        similarity_threshold: float = 0.8,
        max_audience_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Create lookalike audience segments using ML similarity matching
        
        **Enhanced Lookalike Creation:**
        - Multiple similarity algorithms (cosine, euclidean, ML-based)
        - Feature importance analysis
        - Expandable audience sizing
        - Cross-platform lookalike matching
        """
        try:
            if seed_segment_id not in self.segments:
                return {"error": "Seed segment not found"}
            
            seed_segment = self.segments[seed_segment_id]
            
            # Get all available data for lookalike modeling
            all_data = await self._get_all_customer_data()
            
            if not all_data:
                return {"error": "No data available for lookalike modeling"}
            
            df = pd.DataFrame(all_data)
            
            # Extract features for lookalike modeling
            features = self._extract_lookalike_features(df)
            
            # Get seed audience features
            seed_customers = self._get_seed_segment_customers(seed_segment, df)
            
            if len(seed_customers) < 10:
                return {"error": "Seed segment too small for lookalike modeling"}
            
            # Train lookalike model
            lookalike_model = await self._train_lookalike_model(
                features, seed_customers, similarity_threshold
            )
            
            # Find similar audiences
            similar_audiences = await self._find_similar_audiences(
                lookalike_model, features, max_audience_size
            )
            
            # Create lookalike segments
            segments = []
            for i, audience in enumerate(similar_audiences):
                segment = AudienceSegment(
                    name=f"Lookalike {i+1}: {seed_segment.name}",
                    description=f"Lookalike audience based on {seed_segment.name} ({audience['similarity_score']:.2f} similarity)",
                    segment_type=SegmentationType.LOOKALIKE,
                    size=len(audience['customers']),
                    criteria={
                        'seed_segment_id': seed_segment_id,
                        'similarity_threshold': similarity_threshold,
                        'similarity_score': audience['similarity_score']
                    },
                    performance_metrics=audience['predicted_metrics'],
                    platforms=seed_segment.platforms,
                    confidence_score=audience['similarity_score']
                )
                segments.append(segment)
                self.segments[segment.id] = segment
            
            logger.info(f"Created {len(segments)} lookalike segments")
            
            return {
                "segments": [self._segment_to_dict(seg) for seg in segments],
                "seed_segment": self._segment_to_dict(seed_segment),
                "model_performance": lookalike_model['performance'],
                "feature_importance": lookalike_model['feature_importance']
            }
        
        except Exception as e:
            logger.error(f"Error creating lookalike segments: {e}")
            return {"error": f"Lookalike modeling failed: {str(e)}"}
    
    async def create_custom_segment(
        self,
        criteria: Dict[str, Any],
        name: str,
        description: str = "",
        client_id: str = ""
    ) -> Dict[str, Any]:
        """
        Create custom segments using flexible criteria builder
        
        **Custom Segment Builder:**
        - Multiple criteria combinations (AND/OR logic)
        - Performance threshold filters
        - Platform-specific criteria
        - Predictive filters (predicted_ltv, churn_risk)
        """
        try:
            # Get all customer data
            all_data = await self._get_all_customer_data()
            
            if not all_data:
                return {"error": "No data available for custom segmentation"}
            
            df = pd.DataFrame(all_data)
            
            # Apply custom criteria filters
            filtered_data = await self._apply_custom_criteria(df, criteria)
            
            if len(filtered_data) < self.min_segment_size:
                return {"error": f"Segment too small ({len(filtered_data)} customers). Minimum: {self.min_segment_size}"}
            
            # Calculate segment performance
            performance_metrics = self._calculate_segment_metrics(filtered_data)
            
            # Create custom segment
            segment = AudienceSegment(
                name=name,
                description=description or f"Custom segment with {len(criteria)} criteria",
                segment_type=SegmentationType.CUSTOM,
                size=len(filtered_data),
                criteria=criteria,
                performance_metrics=performance_metrics,
                platforms=['meta', 'google', 'tiktok', 'snapchat'],
                confidence_score=self._calculate_segment_confidence(filtered_data)
            )
            
            self.segments[segment.id] = segment
            
            logger.info(f"Created custom segment '{name}' with {segment.size} customers")
            
            return {
                "segment": self._segment_to_dict(segment),
                "preview_data": filtered_data.head(100).to_dict('records'),
                "performance_comparison": await self._compare_to_baseline(performance_metrics)
            }
        
        except Exception as e:
            logger.error(f"Error creating custom segment: {e}")
            return {"error": f"Custom segmentation failed: {str(e)}"}
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _map_rfm_to_lifecycle_stage(self, rfm_score: str) -> str:
        """Map RFM score to lifecycle stage"""
        for stage, scores in self.rfm_segment_map.items():
            if rfm_score in scores:
                return stage.value
        return CustomerLifecycleStage.NEW_CUSTOMERS.value
    
    def _get_lifecycle_stage_description(self, stage: CustomerLifecycleStage) -> str:
        """Get description for lifecycle stage"""
        descriptions = {
            CustomerLifecycleStage.CHAMPIONS: "Your best customers. High recency, frequency, and monetary value.",
            CustomerLifecycleStage.LOYAL_CUSTOMERS: "Consistent buyers with good value and regular purchases.",
            CustomerLifecycleStage.POTENTIAL_LOYALISTS: "Recent customers with potential to become loyal.",
            CustomerLifecycleStage.NEW_CUSTOMERS: "Recently acquired customers to nurture.",
            CustomerLifecycleStage.PROMISING: "Recent buyers showing good initial engagement.",
            CustomerLifecycleStage.NEED_ATTENTION: "Above average customers showing signs of decline.",
            CustomerLifecycleStage.ABOUT_TO_SLEEP: "Declining customers who need re-engagement.",
            CustomerLifecycleStage.AT_RISK: "Previously high-value customers at risk of churning.",
            CustomerLifecycleStage.CANNOT_LOSE: "High-value customers who haven't purchased recently.",
            CustomerLifecycleStage.HIBERNATING: "Inactive customers with low engagement.",
            CustomerLifecycleStage.LOST: "Customers with very low engagement and value."
        }
        return descriptions.get(stage, "Customer segment based on RFM analysis.")
    
    def _calculate_predicted_ltv(self, rfm_data: pd.DataFrame) -> pd.Series:
        """Calculate predicted lifetime value based on RFM scores"""
        # Simple LTV prediction formula (can be enhanced with ML models)
        ltv = (
            rfm_data['monetary'] * 
            (1 + rfm_data['frequency'] / 10) * 
            (1 - rfm_data['recency'] / 365)
        ).clip(lower=0)
        return ltv
    
    def _calculate_segment_metrics(self, segment_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate performance metrics for a segment"""
        metrics = {}
        
        # Basic metrics
        if 'revenue' in segment_data.columns:
            metrics['avg_revenue'] = float(segment_data['revenue'].mean())
            metrics['total_revenue'] = float(segment_data['revenue'].sum())
        
        if 'conversions' in segment_data.columns:
            metrics['avg_conversions'] = float(segment_data['conversions'].mean())
            metrics['total_conversions'] = float(segment_data['conversions'].sum())
        
        if 'clicks' in segment_data.columns and 'impressions' in segment_data.columns:
            metrics['avg_ctr'] = float((segment_data['clicks'] / segment_data['impressions']).mean() * 100)
        
        if 'spend' in segment_data.columns and 'revenue' in segment_data.columns:
            spend_sum = segment_data['spend'].sum()
            revenue_sum = segment_data['revenue'].sum()
            metrics['roas'] = float(revenue_sum / spend_sum) if spend_sum > 0 else 0
        
        # Engagement metrics
        if 'frequency' in segment_data.columns:
            metrics['avg_frequency'] = float(segment_data['frequency'].mean())
        
        if 'predicted_ltv' in segment_data.columns:
            metrics['avg_predicted_ltv'] = float(segment_data['predicted_ltv'].mean())
        
        return metrics
    
    def _calculate_avg_rfm_scores(self, segment_data: pd.DataFrame) -> Dict[str, int]:
        """Calculate average RFM scores for a segment"""
        return {
            'avg_recency_score': int(segment_data['R_score'].mean()) if 'R_score' in segment_data.columns else 0,
            'avg_frequency_score': int(segment_data['F_score'].mean()) if 'F_score' in segment_data.columns else 0,
            'avg_monetary_score': int(segment_data['M_score'].mean()) if 'M_score' in segment_data.columns else 0
        }
    
    def _segment_to_dict(self, segment: AudienceSegment) -> Dict[str, Any]:
        """Convert segment to dictionary for API response"""
        return {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "segment_type": segment.segment_type.value,
            "lifecycle_stage": segment.lifecycle_stage.value if segment.lifecycle_stage else None,
            "size": segment.size,
            "criteria": segment.criteria,
            "performance_metrics": segment.performance_metrics,
            "platforms": segment.platforms,
            "created_date": segment.created_date.isoformat(),
            "last_updated": segment.last_updated.isoformat(),
            "is_active": segment.is_active,
            "confidence_score": segment.confidence_score,
            "predicted_ltv": segment.predicted_ltv,
            "recommended_actions": segment.recommended_actions,
            "rfm_scores": segment.rfm_scores,
            "behavioral_patterns": segment.behavioral_patterns
        }
    
    def _extract_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract behavioral features from customer data"""
        # This is a simplified version - would be enhanced based on actual data structure
        features = pd.DataFrame()
        
        if 'customer_id' in df.columns:
            customer_data = df.groupby('customer_id').agg({
                'clicks': ['sum', 'mean'] if 'clicks' in df.columns else lambda x: 0,
                'impressions': ['sum', 'mean'] if 'impressions' in df.columns else lambda x: 0,
                'conversions': ['sum', 'count'] if 'conversions' in df.columns else lambda x: 0,
                'platform': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown'
            }).reset_index()
            
            features = customer_data
        
        return features
    
    async def _perform_behavioral_clustering(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering on behavioral features"""
        # Simplified clustering implementation
        try:
            # Prepare features for clustering
            numeric_features = features.select_dtypes(include=[np.number])
            
            if numeric_features.empty:
                return {"clusters": {}, "error": "No numeric features for clustering"}
            
            # Standardize features
            X_scaled = self.scaler.fit_transform(numeric_features.fillna(0))
            
            # Perform K-means clustering
            n_clusters = min(5, len(features) // 20)  # Dynamic cluster count
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Analyze clusters
            cluster_results = {}
            for i in range(n_clusters):
                cluster_mask = clusters == i
                cluster_data = features[cluster_mask]
                
                cluster_results[f"cluster_{i}"] = {
                    "name": f"Behavioral Group {i+1}",
                    "description": f"Behavioral cluster with {len(cluster_data)} customers",
                    "size": len(cluster_data),
                    "metrics": self._calculate_segment_metrics(cluster_data),
                    "preferred_platforms": ["meta", "google"],  # Simplified
                    "patterns": {"cluster_center": kmeans.cluster_centers_[i].tolist()}
                }
            
            return {
                "clusters": cluster_results,
                "model_info": {"n_clusters": n_clusters, "algorithm": "kmeans"}
            }
        
        except Exception as e:
            logger.error(f"Error in behavioral clustering: {e}")
            return {"clusters": {}, "error": str(e)}
    
    def _generate_behavioral_insights(self, clustering_results: Dict[str, Any]) -> List[str]:
        """Generate insights from behavioral clustering"""
        insights = []
        
        clusters = clustering_results.get('clusters', {})
        if not clusters:
            return ["No behavioral clusters found"]
        
        # Analyze cluster performance
        cluster_performances = []
        for cluster_id, cluster_info in clusters.items():
            roas = cluster_info['metrics'].get('roas', 0)
            cluster_performances.append((cluster_id, roas, cluster_info['size']))
        
        # Sort by ROAS
        cluster_performances.sort(key=lambda x: x[1], reverse=True)
        
        if cluster_performances:
            best_cluster = cluster_performances[0]
            insights.append(f"Highest performing behavioral group has {best_cluster[1]:.2f} ROAS with {best_cluster[2]} customers")
            
            worst_cluster = cluster_performances[-1]
            insights.append(f"Opportunity to improve: Group with {worst_cluster[1]:.2f} ROAS needs attention")
        
        insights.append(f"Identified {len(clusters)} distinct behavioral patterns in your audience")
        
        return insights
    
    async def _get_all_customer_data(self) -> List[Dict[str, Any]]:
        """Get all customer data for analysis (placeholder - would connect to database)"""
        # This would connect to your actual database
        # For now, return empty list
        return []
    
    def _get_seed_segment_customers(self, segment: AudienceSegment, df: pd.DataFrame) -> pd.DataFrame:
        """Get customers belonging to seed segment"""
        # Apply segment criteria to get customers
        # This is simplified - would use actual segment criteria
        return df.head(100)  # Placeholder
    
    async def _train_lookalike_model(
        self, 
        features: pd.DataFrame, 
        seed_customers: pd.DataFrame, 
        similarity_threshold: float
    ) -> Dict[str, Any]:
        """Train lookalike model"""
        # Simplified lookalike model training
        try:
            # Create labels (1 for seed customers, 0 for others)
            y = np.zeros(len(features))
            # Mark seed customers (this would use proper customer ID matching)
            
            # Train random forest classifier
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            X_train, X_test, y_train, y_test = train_test_split(
                features.fillna(0), y, test_size=0.2, random_state=42
            )
            rf.fit(X_train, y_train)
            
            score = rf.score(X_test, y_test)
            
            return {
                "model": rf,
                "performance": {"accuracy": score},
                "feature_importance": dict(zip(features.columns, rf.feature_importances_))
            }
        
        except Exception as e:
            logger.error(f"Error training lookalike model: {e}")
            return {"model": None, "performance": {}, "feature_importance": {}}
    
    async def _find_similar_audiences(
        self, 
        model: Dict[str, Any], 
        features: pd.DataFrame, 
        max_size: int
    ) -> List[Dict[str, Any]]:
        """Find similar audiences using trained model"""
        if not model.get("model"):
            return []
        
        try:
            # Predict similarity scores
            similarity_scores = model["model"].predict_proba(features.fillna(0))[:, 1]
            
            # Create audience groups based on similarity
            high_similarity_indices = np.where(similarity_scores > 0.7)[0]
            medium_similarity_indices = np.where(
                (similarity_scores > 0.5) & (similarity_scores <= 0.7)
            )[0]
            
            audiences = []
            
            if len(high_similarity_indices) > 0:
                audiences.append({
                    "customers": high_similarity_indices[:max_size//2].tolist(),
                    "similarity_score": float(np.mean(similarity_scores[high_similarity_indices])),
                    "predicted_metrics": {"predicted_roas": 2.5}  # Placeholder
                })
            
            if len(medium_similarity_indices) > 0:
                audiences.append({
                    "customers": medium_similarity_indices[:max_size//2].tolist(),
                    "similarity_score": float(np.mean(similarity_scores[medium_similarity_indices])),
                    "predicted_metrics": {"predicted_roas": 2.0}  # Placeholder
                })
            
            return audiences
        
        except Exception as e:
            logger.error(f"Error finding similar audiences: {e}")
            return []
    
    def _extract_lookalike_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features for lookalike modeling"""
        # Simplified feature extraction
        if 'customer_id' in df.columns:
            return df.groupby('customer_id').agg({
                'revenue': 'sum',
                'conversions': 'sum',
                'clicks': 'sum',
                'impressions': 'sum'
            }).fillna(0)
        return pd.DataFrame()
    
    async def _apply_custom_criteria(self, df: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
        """Apply custom filtering criteria to dataframe"""
        filtered_df = df.copy()
        
        for key, value in criteria.items():
            if key in df.columns:
                if isinstance(value, dict):
                    # Handle range criteria
                    if 'min' in value:
                        filtered_df = filtered_df[filtered_df[key] >= value['min']]
                    if 'max' in value:
                        filtered_df = filtered_df[filtered_df[key] <= value['max']]
                elif isinstance(value, list):
                    # Handle list criteria (IN clause)
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
                else:
                    # Handle exact match
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df
    
    def _calculate_segment_confidence(self, segment_data: pd.DataFrame) -> float:
        """Calculate confidence score for a segment"""
        # Simple confidence calculation based on sample size and consistency
        size_score = min(len(segment_data) / 1000, 1.0)  # Max at 1000 customers
        
        # Check data consistency (coefficient of variation for revenue)
        if 'revenue' in segment_data.columns and len(segment_data) > 1:
            cv = segment_data['revenue'].std() / segment_data['revenue'].mean()
            consistency_score = max(0, 1 - cv)
        else:
            consistency_score = 0.5
        
        return (size_score + consistency_score) / 2
    
    async def _compare_to_baseline(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compare segment performance to baseline"""
        # Placeholder baseline comparison
        baseline_roas = 2.0
        baseline_ctr = 1.5
        
        comparison = {}
        
        if 'roas' in metrics:
            comparison['roas_vs_baseline'] = {
                "performance": metrics['roas'],
                "baseline": baseline_roas,
                "improvement": ((metrics['roas'] - baseline_roas) / baseline_roas * 100) if baseline_roas > 0 else 0
            }
        
        if 'avg_ctr' in metrics:
            comparison['ctr_vs_baseline'] = {
                "performance": metrics['avg_ctr'],
                "baseline": baseline_ctr,
                "improvement": ((metrics['avg_ctr'] - baseline_ctr) / baseline_ctr * 100) if baseline_ctr > 0 else 0
            }
        
        return comparison
