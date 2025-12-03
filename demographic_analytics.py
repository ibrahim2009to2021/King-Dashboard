"""
Week 4: Demographic Analytics Engine
Advanced demographic segmentation and AI-powered insights
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.core.demographic_config import demographic_config
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DemographicInsight:
    """Demographic insight data structure"""
    insight_type: str
    title: str
    description: str
    priority: str
    confidence_score: float
    affected_segments: List[str]
    expected_improvement: float
    recommendation: str
    supporting_data: Dict[str, Any]


class DemographicAnalyticsEngine:
    """
    Comprehensive demographic analytics engine
    
    **Week 4 Demographic Feature**
    - Advanced demographic analysis
    - Performance segmentation
    - Statistical significance testing
    - Opportunity identification
    """
    
    def __init__(self):
        """Initialize demographic analytics engine"""
        self.min_sample_size = demographic_config.MIN_DEMOGRAPHIC_SAMPLE_SIZE
        self.confidence_threshold = demographic_config.INSIGHT_CONFIDENCE_THRESHOLD
        self.target_roas = demographic_config.TARGET_ROAS
        self.target_ctr = demographic_config.TARGET_CTR
        self.target_cvr = demographic_config.TARGET_CVR
        
        # Age group mappings
        self.age_group_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        
        # Performance thresholds for classification
        self.performance_thresholds = {
            'high_performer': {'roas': 3.0, 'ctr': 2.5, 'cvr': 4.0},
            'good_performer': {'roas': 2.0, 'ctr': 1.5, 'cvr': 2.0},
            'underperformer': {'roas': 1.0, 'ctr': 1.0, 'cvr': 1.0}
        }
    
    async def initialize(self) -> bool:
        """Initialize the analytics engine"""
        try:
            logger.info("Demographic analytics engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing demographic analytics engine: {e}")
            return False
    
    def analyze_demographic_performance(
        self,
        demographic_data: List[Dict[str, Any]],
        include_geographic: bool = True,
        include_interests: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive demographic performance analysis
        
        **Week 4 Feature**
        - Multi-dimensional analysis
        - Statistical significance testing
        - Performance benchmarking
        - Opportunity identification
        """
        try:
            if not demographic_data:
                return {"error": "No demographic data provided"}
            
            # Convert to DataFrame
            df = pd.DataFrame(demographic_data)
            
            # Initialize analysis results
            analysis_results = {
                "analysis_date": datetime.now().isoformat(),
                "total_samples": len(df),
                "analysis_summary": {},
                "age_analysis": {},
                "gender_analysis": {},
                "geographic_analysis": {},
                "interest_analysis": {},
                "performance_clusters": {},
                "statistical_insights": [],
                "recommendations": []
            }
            
            # Overall performance summary
            analysis_results["analysis_summary"] = self._calculate_overall_summary(df)
            
            # Age group analysis
            if 'age_group' in df.columns:
                analysis_results["age_analysis"] = self._analyze_age_groups(df)
            
            # Gender analysis
            if 'gender' in df.columns:
                analysis_results["gender_analysis"] = self._analyze_gender_performance(df)
            
            # Geographic analysis
            if include_geographic and 'country' in df.columns:
                analysis_results["geographic_analysis"] = self._analyze_geographic_performance(df)
            
            # Interest analysis
            if include_interests and 'interest_category' in df.columns:
                analysis_results["interest_analysis"] = self._analyze_interest_performance(df)
            
            # Performance clustering
            analysis_results["performance_clusters"] = self._perform_clustering_analysis(df)
            
            # Statistical insights
            analysis_results["statistical_insights"] = self._generate_statistical_insights(df)
            
            logger.info(f"Demographic analysis completed for {len(df)} data points")
            return analysis_results
        
        except Exception as e:
            logger.error(f"Error in demographic analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall performance summary"""
        try:
            # Aggregate metrics
            total_impressions = df['impressions'].sum()
            total_clicks = df['clicks'].sum()
            total_conversions = df['conversions'].sum()
            total_spend = df['spend'].sum()
            total_revenue = df['revenue'].sum()
            
            # Calculate overall rates
            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            overall_roas = (total_revenue / total_spend) if total_spend > 0 else 0
            
            # Performance vs. targets
            ctr_vs_target = overall_ctr / self.target_ctr if self.target_ctr > 0 else 0
            cvr_vs_target = overall_cvr / self.target_cvr if self.target_cvr > 0 else 0
            roas_vs_target = overall_roas / self.target_roas if self.target_roas > 0 else 0
            
            return {
                "total_impressions": int(total_impressions),
                "total_clicks": int(total_clicks),
                "total_conversions": int(total_conversions),
                "total_spend": float(total_spend),
                "total_revenue": float(total_revenue),
                "overall_ctr": round(overall_ctr, 2),
                "overall_cvr": round(overall_cvr, 2),
                "overall_roas": round(overall_roas, 2),
                "performance_vs_targets": {
                    "ctr_performance": round(ctr_vs_target, 2),
                    "cvr_performance": round(cvr_vs_target, 2),
                    "roas_performance": round(roas_vs_target, 2)
                },
                "unique_segments": {
                    "age_groups": df['age_group'].nunique() if 'age_group' in df.columns else 0,
                    "genders": df['gender'].nunique() if 'gender' in df.columns else 0,
                    "countries": df['country'].nunique() if 'country' in df.columns else 0,
                    "interests": df['interest_category'].nunique() if 'interest_category' in df.columns else 0
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating overall summary: {e}")
            return {}
    
    def _analyze_age_groups(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by age groups"""
        try:
            # Aggregate by age group
            age_performance = df.groupby('age_group').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'spend': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calculate rates
            age_performance['ctr'] = (age_performance['clicks'] / age_performance['impressions'] * 100).round(2)
            age_performance['cvr'] = (age_performance['conversions'] / age_performance['clicks'] * 100).round(2)
            age_performance['roas'] = (age_performance['revenue'] / age_performance['spend']).round(2)
            age_performance['cpa'] = (age_performance['spend'] / age_performance['conversions']).round(2)
            
            # Replace inf and NaN values
            age_performance = age_performance.replace([np.inf, -np.inf], 0).fillna(0)
            
            # Rank by performance
            age_performance['roas_rank'] = age_performance['roas'].rank(ascending=False)
            age_performance['ctr_rank'] = age_performance['ctr'].rank(ascending=False)
            age_performance['volume_rank'] = age_performance['impressions'].rank(ascending=False)
            
            # Identify best and worst performers
            best_roas_age = age_performance.loc[age_performance['roas'].idxmax(), 'age_group']
            worst_roas_age = age_performance.loc[age_performance['roas'].idxmin(), 'age_group']
            highest_volume_age = age_performance.loc[age_performance['impressions'].idxmax(), 'age_group']
            
            # Statistical significance tests
            significant_differences = self._test_age_group_significance(df)
            
            return {
                "age_group_performance": age_performance.to_dict('records'),
                "best_performing_age": {
                    "roas_leader": best_roas_age,
                    "highest_volume": highest_volume_age,
                    "worst_roas": worst_roas_age
                },
                "statistical_significance": significant_differences,
                "insights": self._generate_age_insights(age_performance)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing age groups: {e}")
            return {}
    
    def _analyze_gender_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by gender"""
        try:
            # Aggregate by gender
            gender_performance = df.groupby('gender').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'spend': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calculate rates
            gender_performance['ctr'] = (gender_performance['clicks'] / gender_performance['impressions'] * 100).round(2)
            gender_performance['cvr'] = (gender_performance['conversions'] / gender_performance['clicks'] * 100).round(2)
            gender_performance['roas'] = (gender_performance['revenue'] / gender_performance['spend']).round(2)
            
            # Replace inf and NaN values
            gender_performance = gender_performance.replace([np.inf, -np.inf], 0).fillna(0)
            
            # Gender insights
            if len(gender_performance) >= 2:
                gender_differences = self._calculate_gender_differences(gender_performance)
            else:
                gender_differences = {}
            
            return {
                "gender_performance": gender_performance.to_dict('records'),
                "gender_differences": gender_differences,
                "insights": self._generate_gender_insights(gender_performance)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing gender performance: {e}")
            return {}
    
    def _analyze_geographic_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by geographic location"""
        try:
            # Country-level analysis
            country_performance = df.groupby('country').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'spend': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calculate rates
            country_performance['ctr'] = (country_performance['clicks'] / country_performance['impressions'] * 100).round(2)
            country_performance['roas'] = (country_performance['revenue'] / country_performance['spend']).round(2)
            
            # Replace inf and NaN values
            country_performance = country_performance.replace([np.inf, -np.inf], 0).fillna(0)
            
            # Sort by ROAS
            country_performance = country_performance.sort_values('roas', ascending=False)
            
            # Top and bottom performers
            top_countries = country_performance.head(10)
            bottom_countries = country_performance.tail(5)
            
            # Region analysis if available
            region_analysis = {}
            if 'region' in df.columns:
                region_performance = df.groupby(['country', 'region']).agg({
                    'impressions': 'sum',
                    'spend': 'sum',
                    'revenue': 'sum'
                }).reset_index()
                region_performance['roas'] = (region_performance['revenue'] / region_performance['spend']).round(2)
                region_analysis = region_performance.to_dict('records')
            
            return {
                "country_performance": country_performance.to_dict('records'),
                "top_performing_countries": top_countries.to_dict('records'),
                "underperforming_countries": bottom_countries.to_dict('records'),
                "region_analysis": region_analysis,
                "geographic_insights": self._generate_geographic_insights(country_performance)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing geographic performance: {e}")
            return {}
    
    def _analyze_interest_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by interest categories"""
        try:
            # Interest category analysis
            interest_performance = df.groupby('interest_category').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'spend': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calculate performance metrics
            interest_performance['ctr'] = (interest_performance['clicks'] / interest_performance['impressions'] * 100).round(2)
            interest_performance['roas'] = (interest_performance['revenue'] / interest_performance['spend']).round(2)
            interest_performance['efficiency_score'] = (interest_performance['roas'] * interest_performance['ctr']).round(2)
            
            # Replace inf and NaN values
            interest_performance = interest_performance.replace([np.inf, -np.inf], 0).fillna(0)
            
            # Sort by efficiency score
            interest_performance = interest_performance.sort_values('efficiency_score', ascending=False)
            
            # Categorize interests
            high_opportunity = interest_performance[
                (interest_performance['roas'] > self.target_roas) & 
                (interest_performance['impressions'] > self.min_sample_size)
            ]
            
            underperforming = interest_performance[
                interest_performance['roas'] < self.target_roas * 0.5
            ]
            
            return {
                "interest_performance": interest_performance.to_dict('records'),
                "high_opportunity_interests": high_opportunity.to_dict('records'),
                "underperforming_interests": underperforming.to_dict('records'),
                "interest_insights": self._generate_interest_insights(interest_performance)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing interest performance: {e}")
            return {}
    
    def _perform_clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis on demographic segments"""
        try:
            # Prepare features for clustering
            features = ['ctr', 'roas', 'impressions', 'spend']
            available_features = [f for f in features if f in df.columns]
            
            if len(available_features) < 2:
                return {"error": "Insufficient features for clustering"}
            
            # Aggregate data by demographic combination
            clustering_data = df.groupby(['age_group', 'gender']).agg({
                'ctr': 'mean',
                'roas': 'mean',
                'impressions': 'sum',
                'spend': 'sum'
            }).reset_index()
            
            # Prepare features
            X = clustering_data[available_features].fillna(0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform clustering
            n_clusters = min(5, len(clustering_data))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Add cluster labels
            clustering_data['cluster'] = clusters
            
            # Analyze clusters
            cluster_analysis = []
            for cluster_id in range(n_clusters):
                cluster_segments = clustering_data[clustering_data['cluster'] == cluster_id]
                
                cluster_analysis.append({
                    "cluster_id": int(cluster_id),
                    "size": len(cluster_segments),
                    "avg_roas": float(cluster_segments['roas'].mean()),
                    "avg_ctr": float(cluster_segments['ctr'].mean()),
                    "total_spend": float(cluster_segments['spend'].sum()),
                    "segments": cluster_segments[['age_group', 'gender']].to_dict('records'),
                    "performance_tier": self._classify_cluster_performance(cluster_segments)
                })
            
            return {
                "clustering_results": clustering_data.to_dict('records'),
                "cluster_analysis": cluster_analysis,
                "clustering_insights": self._generate_clustering_insights(cluster_analysis)
            }
        
        except Exception as e:
            logger.error(f"Error in clustering analysis: {e}")
            return {}
    
    def _test_age_group_significance(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Test statistical significance between age groups"""
        try:
            age_groups = df['age_group'].unique()
            significant_tests = []
            
            for i, age1 in enumerate(age_groups):
                for age2 in age_groups[i+1:]:
                    group1_data = df[df['age_group'] == age1]['roas']
                    group2_data = df[df['age_group'] == age2]['roas']
                    
                    if len(group1_data) >= 5 and len(group2_data) >= 5:
                        # Perform t-test
                        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
                        
                        if p_value < 0.05:  # Significant difference
                            significant_tests.append({
                                "age_group_1": age1,
                                "age_group_2": age2,
                                "t_statistic": float(t_stat),
                                "p_value": float(p_value),
                                "significant": True,
                                "difference_direction": "higher" if group1_data.mean() > group2_data.mean() else "lower"
                            })
            
            return significant_tests
        
        except Exception as e:
            logger.error(f"Error in significance testing: {e}")
            return []
    
    def _calculate_gender_differences(self, gender_performance: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance differences between genders"""
        try:
            if len(gender_performance) < 2:
                return {}
            
            # Find male and female performance
            male_data = gender_performance[gender_performance['gender'] == 'male']
            female_data = gender_performance[gender_performance['gender'] == 'female']
            
            if len(male_data) == 0 or len(female_data) == 0:
                return {}
            
            male_roas = male_data['roas'].iloc[0]
            female_roas = female_data['roas'].iloc[0]
            male_ctr = male_data['ctr'].iloc[0]
            female_ctr = female_data['ctr'].iloc[0]
            
            return {
                "roas_difference": float(abs(male_roas - female_roas)),
                "roas_better_gender": "male" if male_roas > female_roas else "female",
                "ctr_difference": float(abs(male_ctr - female_ctr)),
                "ctr_better_gender": "male" if male_ctr > female_ctr else "female",
                "male_performance": {
                    "roas": float(male_roas),
                    "ctr": float(male_ctr)
                },
                "female_performance": {
                    "roas": float(female_roas),
                    "ctr": float(female_ctr)
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating gender differences: {e}")
            return {}
    
    def _classify_cluster_performance(self, cluster_data: pd.DataFrame) -> str:
        """Classify cluster performance tier"""
        try:
            avg_roas = cluster_data['roas'].mean()
            avg_ctr = cluster_data['ctr'].mean()
            
            if avg_roas >= self.performance_thresholds['high_performer']['roas']:
                return "high_performer"
            elif avg_roas >= self.performance_thresholds['good_performer']['roas']:
                return "good_performer"
            else:
                return "underperformer"
        
        except Exception:
            return "unknown"
    
    def _generate_statistical_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate statistical insights from the data"""
        try:
            insights = []
            
            # Overall performance distribution
            roas_std = df['roas'].std()
            roas_mean = df['roas'].mean()
            
            if roas_std > roas_mean * 0.5:  # High variability
                insights.append({
                    "type": "variability",
                    "title": "High Performance Variability Detected",
                    "description": f"ROAS varies significantly across segments (std: {roas_std:.2f})",
                    "significance": "high",
                    "recommendation": "Focus on identifying and scaling best-performing segments"
                })
            
            # Segment concentration
            if 'age_group' in df.columns:
                age_concentration = df.groupby('age_group')['spend'].sum()
                top_age_spend = age_concentration.max()
                total_spend = age_concentration.sum()
                
                if top_age_spend / total_spend > 0.6:  # Concentrated spending
                    top_age = age_concentration.idxmax()
                    insights.append({
                        "type": "concentration",
                        "title": "Spending Concentration in Single Age Group",
                        "description": f"60%+ of spend is in {top_age} age group",
                        "significance": "medium",
                        "recommendation": "Consider diversifying to other age groups for growth"
                    })
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating statistical insights: {e}")
            return []
    
    def _generate_age_insights(self, age_performance: pd.DataFrame) -> List[str]:
        """Generate insights about age group performance"""
        insights = []
        
        try:
            # Best performing age group
            best_age = age_performance.loc[age_performance['roas'].idxmax(), 'age_group']
            best_roas = age_performance['roas'].max()
            
            insights.append(f"{best_age} age group shows strongest ROAS performance at {best_roas:.2f}x")
            
            # High volume vs high performance
            highest_volume_age = age_performance.loc[age_performance['impressions'].idxmax(), 'age_group']
            if highest_volume_age != best_age:
                insights.append(f"Opportunity: {best_age} has better ROAS but {highest_volume_age} has higher volume")
            
            # Underperforming segments
            underperforming = age_performance[age_performance['roas'] < self.target_roas]
            if len(underperforming) > 0:
                underperforming_ages = ", ".join(underperforming['age_group'].tolist())
                insights.append(f"Age groups needing optimization: {underperforming_ages}")
        
        except Exception as e:
            logger.error(f"Error generating age insights: {e}")
        
        return insights
    
    def _generate_gender_insights(self, gender_performance: pd.DataFrame) -> List[str]:
        """Generate insights about gender performance"""
        insights = []
        
        try:
            if len(gender_performance) >= 2:
                best_gender = gender_performance.loc[gender_performance['roas'].idxmax(), 'gender']
                best_roas = gender_performance['roas'].max()
                worst_roas = gender_performance['roas'].min()
                
                performance_gap = ((best_roas - worst_roas) / worst_roas) * 100
                
                insights.append(f"{best_gender.title()} audience shows {performance_gap:.1f}% better ROAS")
                
                # Volume vs performance analysis
                highest_volume_gender = gender_performance.loc[gender_performance['impressions'].idxmax(), 'gender']
                if highest_volume_gender != best_gender:
                    insights.append(f"Consider reallocating budget from {highest_volume_gender} to {best_gender}")
        
        except Exception as e:
            logger.error(f"Error generating gender insights: {e}")
        
        return insights
    
    def _generate_geographic_insights(self, country_performance: pd.DataFrame) -> List[str]:
        """Generate insights about geographic performance"""
        insights = []
        
        try:
            # Top performer
            top_country = country_performance.iloc[0]['country']
            top_roas = country_performance.iloc[0]['roas']
            
            insights.append(f"{top_country} leads with {top_roas:.2f}x ROAS")
            
            # Expansion opportunities
            high_roas_countries = country_performance[
                (country_performance['roas'] > self.target_roas) & 
                (country_performance['spend'] < country_performance['spend'].quantile(0.7))
            ]
            
            if len(high_roas_countries) > 0:
                expansion_countries = high_roas_countries['country'].head(3).tolist()
                insights.append(f"Expansion opportunities: {', '.join(expansion_countries)}")
            
            # Underperforming markets
            underperforming = country_performance[country_performance['roas'] < self.target_roas * 0.5]
            if len(underperforming) > 0:
                underperforming_countries = underperforming['country'].head(3).tolist()
                insights.append(f"Markets needing attention: {', '.join(underperforming_countries)}")
        
        except Exception as e:
            logger.error(f"Error generating geographic insights: {e}")
        
        return insights
    
    def _generate_interest_insights(self, interest_performance: pd.DataFrame) -> List[str]:
        """Generate insights about interest category performance"""
        insights = []
        
        try:
            # Top performing interest
            top_interest = interest_performance.iloc[0]['interest_category']
            top_efficiency = interest_performance.iloc[0]['efficiency_score']
            
            insights.append(f"'{top_interest}' shows highest efficiency score: {top_efficiency:.2f}")
            
            # High opportunity interests
            high_opportunity = interest_performance[
                (interest_performance['roas'] > self.target_roas) & 
                (interest_performance['impressions'] > self.min_sample_size)
            ]
            
            if len(high_opportunity) > 0:
                opportunity_interests = high_opportunity['interest_category'].head(3).tolist()
                insights.append(f"Scale these high-performing interests: {', '.join(opportunity_interests)}")
        
        except Exception as e:
            logger.error(f"Error generating interest insights: {e}")
        
        return insights
    
    def _generate_clustering_insights(self, cluster_analysis: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from clustering analysis"""
        insights = []
        
        try:
            # High performers
            high_performers = [c for c in cluster_analysis if c['performance_tier'] == 'high_performer']
            if high_performers:
                high_performer_size = sum(c['size'] for c in high_performers)
                insights.append(f"{high_performer_size} high-performing segments identified for scaling")
            
            # Underperformers
            underperformers = [c for c in cluster_analysis if c['performance_tier'] == 'underperformer']
            if underperformers:
                underperformer_size = sum(c['size'] for c in underperformers)
                insights.append(f"{underperformer_size} underperforming segments need optimization")
        
        except Exception as e:
            logger.error(f"Error generating clustering insights: {e}")
        
        return insights


class DemographicInsightsGenerator:
    """
    AI-powered insights generator for demographic analysis
    
    **Week 4 Feature**
    - Automated insight generation
    - Priority scoring
    - Recommendation engine
    """
    
    def __init__(self):
        """Initialize insights generator"""
        self.confidence_threshold = demographic_config.INSIGHT_CONFIDENCE_THRESHOLD
        self.min_improvement_threshold = 10.0  # Minimum 10% improvement potential
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> List[DemographicInsight]:
        """Generate AI-powered demographic insights"""
        try:
            insights = []
            
            # Age group insights
            if 'age_analysis' in analysis_results:
                age_insights = self._generate_age_insights(analysis_results['age_analysis'])
                insights.extend(age_insights)
            
            # Gender insights
            if 'gender_analysis' in analysis_results:
                gender_insights = self._generate_gender_insights(analysis_results['gender_analysis'])
                insights.extend(gender_insights)
            
            # Geographic insights
            if 'geographic_analysis' in analysis_results:
                geo_insights = self._generate_geographic_insights(analysis_results['geographic_analysis'])
                insights.extend(geo_insights)
            
            # Performance insights
            if 'performance_clusters' in analysis_results:
                cluster_insights = self._generate_cluster_insights(analysis_results['performance_clusters'])
                insights.extend(cluster_insights)
            
            # Sort by priority and confidence
            insights.sort(key=lambda x: (
                {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.priority],
                x.confidence_score
            ), reverse=True)
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    def _generate_age_insights(self, age_analysis: Dict[str, Any]) -> List[DemographicInsight]:
        """Generate age-specific insights"""
        insights = []
        
        try:
            if 'age_group_performance' not in age_analysis:
                return insights
            
            performance_data = age_analysis['age_group_performance']
            
            # Find best and worst performers
            best_performer = max(performance_data, key=lambda x: x['roas'])
            worst_performer = min(performance_data, key=lambda x: x['roas'])
            
            # Opportunity insight
            if best_performer['roas'] > worst_performer['roas'] * 1.5:
                improvement_potential = ((best_performer['roas'] - worst_performer['roas']) / worst_performer['roas']) * 100
                
                insights.append(DemographicInsight(
                    insight_type="opportunity",
                    title=f"High-Impact Age Group Optimization Opportunity",
                    description=f"{best_performer['age_group']} outperforms {worst_performer['age_group']} by {improvement_potential:.1f}%",
                    priority="high",
                    confidence_score=0.9,
                    affected_segments=[worst_performer['age_group']],
                    expected_improvement=improvement_potential,
                    recommendation=f"Reallocate budget from {worst_performer['age_group']} to {best_performer['age_group']} targeting",
                    supporting_data={
                        "best_age_roas": best_performer['roas'],
                        "worst_age_roas": worst_performer['roas'],
                        "potential_improvement": improvement_potential
                    }
                ))
        
        except Exception as e:
            logger.error(f"Error generating age insights: {e}")
        
        return insights
    
    def _generate_gender_insights(self, gender_analysis: Dict[str, Any]) -> List[DemographicInsight]:
        """Generate gender-specific insights"""
        insights = []
        
        try:
            if 'gender_differences' not in gender_analysis:
                return insights
            
            gender_diff = gender_analysis['gender_differences']
            
            if 'roas_difference' in gender_diff and gender_diff['roas_difference'] > 0.5:
                better_gender = gender_diff['roas_better_gender']
                improvement_potential = (gender_diff['roas_difference'] / min(
                    gender_diff['male_performance']['roas'],
                    gender_diff['female_performance']['roas']
                )) * 100
                
                insights.append(DemographicInsight(
                    insight_type="optimization",
                    title=f"Gender Targeting Performance Gap",
                    description=f"{better_gender.title()} audience shows significantly better ROAS performance",
                    priority="medium",
                    confidence_score=0.8,
                    affected_segments=[better_gender],
                    expected_improvement=improvement_potential,
                    recommendation=f"Increase budget allocation to {better_gender} targeting",
                    supporting_data=gender_diff
                ))
        
        except Exception as e:
            logger.error(f"Error generating gender insights: {e}")
        
        return insights
    
    def _generate_geographic_insights(self, geo_analysis: Dict[str, Any]) -> List[DemographicInsight]:
        """Generate geographic insights"""
        insights = []
        
        try:
            if 'top_performing_countries' not in geo_analysis:
                return insights
            
            top_countries = geo_analysis['top_performing_countries']
            
            # Expansion opportunity
            if len(top_countries) > 0:
                top_performer = top_countries[0]
                
                if top_performer['roas'] > 2.0 and top_performer['spend'] < 10000:  # High ROAS, low spend
                    insights.append(DemographicInsight(
                        insight_type="opportunity",
                        title=f"Geographic Expansion Opportunity",
                        description=f"{top_performer['country']} shows excellent ROAS with room for growth",
                        priority="high",
                        confidence_score=0.85,
                        affected_segments=[top_performer['country']],
                        expected_improvement=50.0,
                        recommendation=f"Increase budget allocation to {top_performer['country']}",
                        supporting_data={
                            "country": top_performer['country'],
                            "current_roas": top_performer['roas'],
                            "current_spend": top_performer['spend']
                        }
                    ))
        
        except Exception as e:
            logger.error(f"Error generating geographic insights: {e}")
        
        return insights
    
    def _generate_cluster_insights(self, cluster_analysis: Dict[str, Any]) -> List[DemographicInsight]:
        """Generate cluster-based insights"""
        insights = []
        
        try:
            if 'cluster_analysis' not in cluster_analysis:
                return insights
            
            clusters = cluster_analysis['cluster_analysis']
            
            # Find high-performing clusters
            high_performers = [c for c in clusters if c['performance_tier'] == 'high_performer']
            
            if high_performers:
                total_high_performer_segments = sum(c['size'] for c in high_performers)
                
                insights.append(DemographicInsight(
                    insight_type="scaling",
                    title="High-Performing Segment Clusters Identified",
                    description=f"Found {total_high_performer_segments} demographic segments with superior performance",
                    priority="high",
                    confidence_score=0.9,
                    affected_segments=[f"Cluster {c['cluster_id']}" for c in high_performers],
                    expected_improvement=30.0,
                    recommendation="Scale budget allocation to these high-performing demographic combinations",
                    supporting_data={
                        "high_performer_clusters": high_performers,
                        "total_segments": total_high_performer_segments
                    }
                ))
        
        except Exception as e:
            logger.error(f"Error generating cluster insights: {e}")
        
        return insights
