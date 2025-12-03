"""
Week 4: Demographic Segmentation Routes
Advanced demographic analysis and AI-powered insights
"""

from datetime import datetime, date, timedelta
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.demographic_config import demographic_config
from app.db.models import User, DemographicSegment, AudienceInsight
from app.schemas.demographic_schemas import (
    DemographicSegmentResponse,
    DemographicAnalysisRequest,
    DemographicAnalysisResponse,
    AudienceInsightResponse,
    DemographicSyncRequest,
    GeographicPerformanceResponse,
    DemographicTrendsResponse,
    DemographicExportRequest
)
from analytics.demographic_analytics import DemographicAnalyticsEngine, DemographicInsightsGenerator
from api_clients.demographic_clients import UnifiedDemographicClient
from workers.demographic_sync_tasks import (
    sync_demographic_data_task,
    daily_demographic_sync_task,
    generate_insights_task
)

router = APIRouter()


@router.get("/segments", response_model=List[DemographicSegmentResponse])
async def get_demographic_segments(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    age_group: Optional[str] = Query(None, description="Filter by age group"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    country: Optional[str] = Query(None, description="Filter by country"),
    start_date: Optional[date] = Query(None, description="Filter segments after this date"),
    end_date: Optional[date] = Query(None, description="Filter segments before this date"),
    min_impressions: int = Query(100, description="Minimum impressions threshold"),
    sort_by: str = Query("roas", description="Sort by metric (roas, ctr, spend, revenue)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get demographic segments with filtering and sorting
    
    **Week 4 Demographic Feature**
    - Advanced demographic data retrieval
    - Multi-dimensional filtering
    - Performance-based sorting
    - Age, gender, location analysis
    """
    
    # Base query
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.impressions >= min_impressions
        )
    )
    
    # Apply filters
    if platform:
        query = query.filter(DemographicSegment.platform == platform)
    
    if age_group:
        query = query.filter(DemographicSegment.age_group == age_group)
    
    if gender:
        query = query.filter(DemographicSegment.gender == gender)
    
    if country:
        query = query.filter(DemographicSegment.country == country)
    
    if start_date:
        query = query.filter(DemographicSegment.date >= start_date)
    
    if end_date:
        query = query.filter(DemographicSegment.date <= end_date)
    
    # Apply sorting
    sort_column = getattr(DemographicSegment, sort_by, DemographicSegment.roas)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    segments = query.offset(skip).limit(limit).all()
    
    return segments


@router.post("/analyze", response_model=DemographicAnalysisResponse)
async def analyze_demographics(
    analysis_request: DemographicAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Perform comprehensive demographic analysis
    
    **Week 4 Demographic Feature**
    - Advanced demographic analytics
    - AI-powered insights generation
    - Multi-platform analysis
    - Performance optimization recommendations
    """
    
    # Validate date range
    if analysis_request.start_date >= analysis_request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Check if date range is not too large
    date_diff = (analysis_request.end_date - analysis_request.start_date).days
    if date_diff > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 365 days"
        )
    
    # Get demographic data
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.date.between(analysis_request.start_date, analysis_request.end_date),
            DemographicSegment.impressions >= analysis_request.min_impressions
        )
    )
    
    # Apply platform filter
    if analysis_request.platforms:
        query = query.filter(DemographicSegment.platform.in_(analysis_request.platforms))
    
    segments = query.all()
    
    if not segments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No demographic data found for the specified criteria"
        )
    
    # Convert to data format for analysis
    segment_data = []
    for segment in segments:
        segment_data.append({
            "platform": segment.platform,
            "date": segment.date,
            "age_group": segment.age_group,
            "gender": segment.gender,
            "country": segment.country,
            "region": segment.region,
            "city": segment.city,
            "interest_category": segment.interest_category,
            "impressions": segment.impressions,
            "clicks": segment.clicks,
            "conversions": segment.conversions,
            "spend": segment.spend,
            "revenue": segment.revenue,
            "roas": segment.roas,
            "ctr": segment.ctr,
            "cvr": segment.cvr
        })
    
    # Initialize analytics engine
    analytics_engine = DemographicAnalyticsEngine()
    insights_generator = DemographicInsightsGenerator()
    
    # Perform analysis
    analysis_results = analytics_engine.analyze_demographic_performance(
        demographic_data=segment_data,
        include_geographic=analysis_request.include_geographic,
        include_interests=analysis_request.include_interests
    )
    
    # Generate AI insights
    insights = insights_generator.generate_insights(analysis_results)
    
    return {
        "analysis_date": datetime.utcnow(),
        "date_range": {
            "start_date": analysis_request.start_date,
            "end_date": analysis_request.end_date
        },
        "total_segments_analyzed": len(segments),
        "platforms_analyzed": analysis_request.platforms or ["all"],
        "analysis_results": analysis_results,
        "insights": insights,
        "summary_statistics": {
            "total_impressions": sum(s.impressions for s in segments),
            "total_spend": sum(s.spend for s in segments),
            "total_revenue": sum(s.revenue for s in segments),
            "overall_roas": sum(s.revenue for s in segments) / sum(s.spend for s in segments) if sum(s.spend for s in segments) > 0 else 0,
            "unique_age_groups": len(set(s.age_group for s in segments if s.age_group)),
            "unique_genders": len(set(s.gender for s in segments if s.gender)),
            "unique_countries": len(set(s.country for s in segments if s.country))
        }
    }


@router.get("/insights", response_model=List[AudienceInsightResponse])
async def get_audience_insights(
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query("new", description="Filter by status"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get AI-generated audience insights
    
    **Week 4 Demographic Feature**
    - AI-powered demographic insights
    - Performance optimization recommendations
    - Audience opportunity identification
    - Priority-based filtering
    """
    
    # Base query
    query = db.query(AudienceInsight).filter(
        AudienceInsight.client_id == current_user.client_id
    )
    
    # Apply filters
    if insight_type:
        query = query.filter(AudienceInsight.insight_type == insight_type)
    
    if priority:
        query = query.filter(AudienceInsight.priority == priority)
    
    if status:
        query = query.filter(AudienceInsight.status == status)
    
    if platform:
        query = query.filter(AudienceInsight.platform == platform)
    
    # Order by priority and creation date
    priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
    insights = query.order_by(
        AudienceInsight.priority.case(priority_order),
        desc(AudienceInsight.created_at)
    ).offset(skip).limit(limit).all()
    
    return insights


@router.post("/sync")
async def sync_demographic_data(
    sync_request: DemographicSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Sync demographic data from advertising platforms
    
    **Week 4 Demographic Feature**
    - Multi-platform demographic sync
    - Real-time data synchronization
    - Background processing
    - Data quality validation
    """
    
    # Validate platforms
    valid_platforms = ["meta", "google", "tiktok", "snapchat"]
    invalid_platforms = [p for p in sync_request.platforms if p not in valid_platforms]
    if invalid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platforms: {invalid_platforms}"
        )
    
    # Validate date range
    date_diff = (sync_request.end_date - sync_request.start_date).days
    if date_diff > demographic_config.MAX_SYNC_DATE_RANGE_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Date range cannot exceed {demographic_config.MAX_SYNC_DATE_RANGE_DAYS} days"
        )
    
    # Schedule sync tasks for each platform
    task_ids = []
    for platform in sync_request.platforms:
        task = sync_demographic_data_task.delay(
            str(current_user.client_id),
            platform,
            sync_request.start_date.isoformat(),
            sync_request.end_date.isoformat(),
            force_refresh=sync_request.force_refresh
        )
        task_ids.append(task.id)
    
    return {
        "message": "Demographic data sync initiated",
        "client_id": current_user.client_id,
        "platforms": sync_request.platforms,
        "date_range": {
            "start_date": sync_request.start_date,
            "end_date": sync_request.end_date
        },
        "task_ids": task_ids,
        "estimated_completion": datetime.utcnow() + timedelta(minutes=len(sync_request.platforms) * 10)
    }


@router.get("/geographic", response_model=List[GeographicPerformanceResponse])
async def get_geographic_performance(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    country: Optional[str] = Query(None, description="Filter by country"),
    region: Optional[str] = Query(None, description="Filter by region"),
    start_date: Optional[date] = Query(None, description="Filter after this date"),
    end_date: Optional[date] = Query(None, description="Filter before this date"),
    sort_by: str = Query("roas", description="Sort by metric"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get geographic performance data
    
    **Week 4 Demographic Feature**
    - Location-based performance analysis
    - Geographic optimization insights
    - Country, region, city breakdowns
    - ROI by location
    """
    
    # Set default date range
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Aggregate geographic performance
    query = db.query(
        DemographicSegment.country,
        DemographicSegment.region,
        DemographicSegment.city,
        DemographicSegment.platform,
        func.sum(DemographicSegment.impressions).label('impressions'),
        func.sum(DemographicSegment.clicks).label('clicks'),
        func.sum(DemographicSegment.conversions).label('conversions'),
        func.sum(DemographicSegment.spend).label('spend'),
        func.sum(DemographicSegment.revenue).label('revenue'),
        (func.sum(DemographicSegment.revenue) / func.sum(DemographicSegment.spend)).label('roas'),
        (func.sum(DemographicSegment.clicks) / func.sum(DemographicSegment.impressions) * 100).label('ctr')
    ).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.date.between(start_date, end_date),
            DemographicSegment.country.isnot(None)
        )
    ).group_by(
        DemographicSegment.country,
        DemographicSegment.region,
        DemographicSegment.city,
        DemographicSegment.platform
    )
    
    # Apply filters
    if platform:
        query = query.filter(DemographicSegment.platform == platform)
    
    if country:
        query = query.filter(DemographicSegment.country == country)
    
    if region:
        query = query.filter(DemographicSegment.region == region)
    
    # Apply sorting
    if sort_by == "roas":
        query = query.order_by(desc('roas'))
    elif sort_by == "spend":
        query = query.order_by(desc('spend'))
    elif sort_by == "revenue":
        query = query.order_by(desc('revenue'))
    else:
        query = query.order_by(desc('roas'))
    
    # Apply limit
    results = query.limit(limit).all()
    
    # Convert to response format
    geographic_data = []
    for result in results:
        geographic_data.append({
            "country": result.country,
            "region": result.region,
            "city": result.city,
            "platform": result.platform,
            "impressions": result.impressions,
            "clicks": result.clicks,
            "conversions": result.conversions,
            "spend": float(result.spend),
            "revenue": float(result.revenue),
            "roas": float(result.roas) if result.roas else 0,
            "ctr": float(result.ctr) if result.ctr else 0
        })
    
    return geographic_data


@router.get("/trends", response_model=DemographicTrendsResponse)
async def get_demographic_trends(
    demographic_type: str = Query(..., description="Type of demographic (age, gender, location)"),
    period_type: str = Query("weekly", description="Period type (daily, weekly, monthly)"),
    platforms: List[str] = Query(["meta", "google"], description="Platforms to analyze"),
    lookback_days: int = Query(90, description="Days to look back for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get demographic performance trends
    
    **Week 4 Demographic Feature**
    - Trend analysis over time
    - Performance changes detection
    - Seasonal pattern identification
    - Forecasting insights
    """
    
    # Validate inputs
    valid_demographic_types = ["age", "gender", "location", "interest"]
    if demographic_type not in valid_demographic_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid demographic type. Must be one of: {valid_demographic_types}"
        )
    
    valid_period_types = ["daily", "weekly", "monthly"]
    if period_type not in valid_period_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period type. Must be one of: {valid_period_types}"
        )
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)
    
    # Get demographic data
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.date.between(start_date, end_date),
            DemographicSegment.platform.in_(platforms)
        )
    )
    
    segments = query.all()
    
    if not segments:
        return {
            "demographic_type": demographic_type,
            "period_type": period_type,
            "date_range": {"start_date": start_date, "end_date": end_date},
            "trends": [],
            "message": "No data found for trend analysis"
        }
    
    # Group data by demographic and time period
    trends = {}
    
    for segment in segments:
        # Determine demographic value
        if demographic_type == "age":
            demo_value = segment.age_group
        elif demographic_type == "gender":
            demo_value = segment.gender
        elif demographic_type == "location":
            demo_value = segment.country
        elif demographic_type == "interest":
            demo_value = segment.interest_category
        
        if not demo_value:
            continue
        
        # Determine time period
        if period_type == "daily":
            time_key = segment.date.isoformat()
        elif period_type == "weekly":
            week_start = segment.date - timedelta(days=segment.date.weekday())
            time_key = week_start.isoformat()
        elif period_type == "monthly":
            time_key = f"{segment.date.year}-{segment.date.month:02d}"
        
        # Initialize nested dict
        if demo_value not in trends:
            trends[demo_value] = {}
        if time_key not in trends[demo_value]:
            trends[demo_value][time_key] = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "spend": 0,
                "revenue": 0
            }
        
        # Aggregate metrics
        trends[demo_value][time_key]["impressions"] += segment.impressions
        trends[demo_value][time_key]["clicks"] += segment.clicks
        trends[demo_value][time_key]["conversions"] += segment.conversions
        trends[demo_value][time_key]["spend"] += segment.spend
        trends[demo_value][time_key]["revenue"] += segment.revenue
    
    # Calculate rates and trends for each demographic
    trend_data = []
    for demo_value, time_periods in trends.items():
        periods = sorted(time_periods.keys())
        
        # Calculate performance metrics for each period
        period_data = []
        for period in periods:
            metrics = time_periods[period]
            roas = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
            ctr = metrics["clicks"] / metrics["impressions"] * 100 if metrics["impressions"] > 0 else 0
            
            period_data.append({
                "period": period,
                "impressions": metrics["impressions"],
                "spend": metrics["spend"],
                "revenue": metrics["revenue"],
                "roas": roas,
                "ctr": ctr
            })
        
        # Calculate trend direction and strength
        if len(period_data) >= 2:
            first_roas = period_data[0]["roas"]
            last_roas = period_data[-1]["roas"]
            
            if last_roas > first_roas * 1.1:
                trend_direction = "improving"
            elif last_roas < first_roas * 0.9:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"
        
        trend_data.append({
            "demographic_value": demo_value,
            "trend_direction": trend_direction,
            "period_data": period_data
        })
    
    return {
        "demographic_type": demographic_type,
        "period_type": period_type,
        "date_range": {"start_date": start_date, "end_date": end_date},
        "platforms": platforms,
        "trends": trend_data
    }


@router.put("/insights/{insight_id}/status")
async def update_insight_status(
    insight_id: str,
    status: str = Query(..., description="New status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update audience insight status
    
    **Week 4 Demographic Feature**
    - Insight lifecycle management
    - Implementation tracking
    - Feedback collection
    """
    
    # Validate status
    valid_statuses = ["new", "reviewed", "implemented", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # Get insight
    insight = db.query(AudienceInsight).filter(
        and_(
            AudienceInsight.id == insight_id,
            AudienceInsight.client_id == current_user.client_id
        )
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience insight not found"
        )
    
    # Update status
    insight.status = status
    insight.updated_at = datetime.utcnow()
    
    if status == "reviewed":
        insight.reviewed_by = current_user.id
        insight.reviewed_at = datetime.utcnow()
    elif status == "implemented":
        insight.implemented_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Insight status updated successfully",
        "insight_id": insight_id,
        "new_status": status,
        "updated_at": insight.updated_at
    }


@router.get("/export/segments")
async def export_demographic_segments(
    format: str = Query("csv", description="Export format (csv, excel, pdf)"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    start_date: Optional[date] = Query(None, description="Filter after this date"),
    end_date: Optional[date] = Query(None, description="Filter before this date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Export demographic segments data
    
    **Week 4 Demographic Feature**
    - Data export functionality
    - Multiple export formats
    - Filtered data export
    - Large dataset support
    """
    
    # Validate format
    valid_formats = ["csv", "excel", "pdf"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format. Must be one of: {valid_formats}"
        )
    
    # Set default date range
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Get segments for export
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.date.between(start_date, end_date)
        )
    )
    
    if platform:
        query = query.filter(DemographicSegment.platform == platform)
    
    # Limit export size
    max_records = demographic_config.MAX_EXPORT_ROWS
    total_records = query.count()
    
    if total_records > max_records:
        segments = query.limit(max_records).all()
        truncated = True
    else:
        segments = query.all()
        truncated = False
    
    return {
        "message": "Export data prepared",
        "format": format,
        "total_records": total_records,
        "exported_records": len(segments),
        "truncated": truncated,
        "date_range": {"start_date": start_date, "end_date": end_date},
        "platform": platform,
        "sample_data": [
            {
                "date": segment.date,
                "platform": segment.platform,
                "age_group": segment.age_group,
                "gender": segment.gender,
                "country": segment.country,
                "impressions": segment.impressions,
                "clicks": segment.clicks,
                "conversions": segment.conversions,
                "spend": segment.spend,
                "revenue": segment.revenue,
                "roas": segment.roas,
                "ctr": segment.ctr
            } for segment in segments[:5]  # Sample first 5 records
        ]
    }


@router.get("/benchmarks")
async def get_demographic_benchmarks(
    demographic_type: str = Query("age", description="Demographic type for benchmarks"),
    platform: Optional[str] = Query(None, description="Platform for benchmarks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get demographic performance benchmarks
    
    **Week 4 Demographic Feature**
    - Industry benchmarks
    - Performance comparisons
    - Best practice insights
    - Competitive analysis
    """
    
    # Calculate benchmarks from user's historical data
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.date >= date.today() - timedelta(days=90)
        )
    )
    
    if platform:
        query = query.filter(DemographicSegment.platform == platform)
    
    segments = query.all()
    
    if not segments:
        return {
            "demographic_type": demographic_type,
            "platform": platform,
            "benchmarks": {},
            "message": "Insufficient data for benchmark calculation"
        }
    
    # Calculate benchmarks by demographic type
    benchmarks = {}
    
    if demographic_type == "age":
        age_groups = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        for age_group in age_groups:
            age_segments = [s for s in segments if s.age_group == age_group]
            if age_segments:
                benchmarks[age_group] = {
                    "avg_roas": sum(s.roas for s in age_segments if s.roas) / len([s for s in age_segments if s.roas]),
                    "avg_ctr": sum(s.ctr for s in age_segments if s.ctr) / len([s for s in age_segments if s.ctr]),
                    "total_impressions": sum(s.impressions for s in age_segments),
                    "sample_size": len(age_segments)
                }
    
    elif demographic_type == "gender":
        genders = ["male", "female", "unknown"]
        for gender in genders:
            gender_segments = [s for s in segments if s.gender == gender]
            if gender_segments:
                benchmarks[gender] = {
                    "avg_roas": sum(s.roas for s in gender_segments if s.roas) / len([s for s in gender_segments if s.roas]),
                    "avg_ctr": sum(s.ctr for s in gender_segments if s.ctr) / len([s for s in gender_segments if s.ctr]),
                    "total_impressions": sum(s.impressions for s in gender_segments),
                    "sample_size": len(gender_segments)
                }
    
    # Industry benchmarks for comparison
    industry_benchmarks = {
        "target_roas": demographic_config.TARGET_ROAS,
        "target_ctr": demographic_config.TARGET_CTR,
        "target_cvr": demographic_config.TARGET_CVR
    }
    
    return {
        "demographic_type": demographic_type,
        "platform": platform,
        "user_benchmarks": benchmarks,
        "industry_benchmarks": industry_benchmarks,
        "calculation_period_days": 90,
        "total_segments_analyzed": len(segments)
    }


@router.get("/interests")
async def get_interest_categories(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    parent_category: Optional[str] = Query(None, description="Filter by parent category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get interest category performance
    
    **Week 4 Demographic Feature**
    - Interest category analysis
    - Performance by interest
    - Targeting optimization
    - Audience expansion opportunities
    """
    
    # Get interest performance data
    query = db.query(DemographicSegment).filter(
        and_(
            DemographicSegment.client_id == current_user.client_id,
            DemographicSegment.interest_category.isnot(None),
            DemographicSegment.date >= date.today() - timedelta(days=30)
        )
    )
    
    if platform:
        query = query.filter(DemographicSegment.platform == platform)
    
    segments = query.all()
    
    # Group by interest category
    interest_performance = {}
    for segment in segments:
        interest = segment.interest_category
        if interest not in interest_performance:
            interest_performance[interest] = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "spend": 0,
                "revenue": 0
            }
        
        interest_performance[interest]["impressions"] += segment.impressions
        interest_performance[interest]["clicks"] += segment.clicks
        interest_performance[interest]["conversions"] += segment.conversions
        interest_performance[interest]["spend"] += segment.spend
        interest_performance[interest]["revenue"] += segment.revenue
    
    # Calculate performance metrics
    interest_data = []
    for interest, metrics in interest_performance.items():
        roas = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
        ctr = metrics["clicks"] / metrics["impressions"] * 100 if metrics["impressions"] > 0 else 0
        
        interest_data.append({
            "interest_category": interest,
            "impressions": metrics["impressions"],
            "spend": metrics["spend"],
            "revenue": metrics["revenue"],
            "roas": roas,
            "ctr": ctr,
            "performance_score": (roas * ctr) / 100  # Combined performance score
        })
    
    # Sort by performance score
    interest_data.sort(key=lambda x: x["performance_score"], reverse=True)
    
    return {
        "platform": platform,
        "total_interests": len(interest_data),
        "analysis_period_days": 30,
        "interest_performance": interest_data[:50]  # Top 50 interests
    }
