"""
Credit Scoring Service with Database Aggregations
Replaces hardcoded mock values with real aggregation-pipeline-based scoring.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

from ..core.database import db
from ..common.utils import generate_id, now_iso

logger = logging.getLogger(__name__)


class CreditScoringService:
    """
    Production credit scoring using MongoDB aggregation pipelines.
    
    Features:
    - Real-time buyer payment behavior analysis
    - Company creditworthiness scoring
    - Historical trend analysis
    - Full audit trail for regulatory compliance
    """
    
    @staticmethod
    async def calculate_buyer_score(
        buyer_id: str,
        company_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate buyer credit score using aggregation pipeline.
        
        Scoring factors:
        - Payment timeliness (40%)
        - Order volume consistency (20%)
        - Payment amount reliability (20%)
        - Relationship length (10%)
        - Recent behavior trend (10%)
        """
        scoring_id = generate_id()
        
        # Aggregation pipeline for buyer payment analysis
        pipeline = [
            # Match payments for this buyer
            {"$match": {
                "buyer_id": buyer_id,
                "company_id": company_id
            }},
            # Calculate payment metrics
            {"$group": {
                "_id": "$buyer_id",
                "total_payments": {"$sum": 1},
                "total_amount": {"$sum": {"$ifNull": ["$amount", 0]}},
                "avg_amount": {"$avg": {"$ifNull": ["$amount", 0]}},
                "on_time_count": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["paid", "on_time", "received", "completed"]]},
                            1,
                            0
                        ]
                    }
                },
                "delayed_count": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "delayed"]}, 1, 0]
                    }
                },
                "first_payment": {"$min": "$created_at"},
                "last_payment": {"$max": "$created_at"},
                "payment_amounts": {"$push": "$amount"}
            }},
            # Calculate derived metrics
            {"$project": {
                "total_payments": 1,
                "total_amount": 1,
                "avg_amount": 1,
                "on_time_count": 1,
                "delayed_count": 1,
                "first_payment": 1,
                "last_payment": 1,
                "on_time_rate": {
                    "$cond": [
                        {"$gt": ["$total_payments", 0]},
                        {"$divide": ["$on_time_count", "$total_payments"]},
                        0
                    ]
                },
                "payment_consistency": {
                    "$cond": [
                        {"$gt": [{"$size": "$payment_amounts"}, 1]},
                        {"$stdDevPop": "$payment_amounts"},
                        0
                    ]
                }
            }}
        ]
        
        result = await db.payments.aggregate(pipeline).to_list(1)
        
        if not result:
            # No payment history - return neutral score
            score_data = {
                "buyer_id": buyer_id,
                "credit_score": 600,  # Neutral score
                "risk_level": "unknown",
                "payment_history": {"on_time": 0, "delayed": 0, "total": 0},
                "recommendation": "No payment history. Consider advance payment terms.",
                "scoring_basis": "no_data"
            }
        else:
            metrics = result[0]
            
            # Calculate component scores
            on_time_rate = metrics.get("on_time_rate", 0)
            total_payments = metrics.get("total_payments", 0)
            
            # Payment timeliness score (0-400 points)
            timeliness_score = int(on_time_rate * 400)
            
            # Volume consistency score (0-200 points)
            volume_score = min(200, total_payments * 20)  # Cap at 200
            
            # Amount reliability score (0-200 points)
            consistency = metrics.get("payment_consistency", 0)
            avg_amount = metrics.get("avg_amount", 0)
            reliability_score = 200 if consistency == 0 else max(0, 200 - int((consistency / avg_amount) * 100)) if avg_amount > 0 else 100
            
            # Relationship length score (0-100 points)
            first_payment = metrics.get("first_payment")
            if first_payment:
                try:
                    first_date = datetime.fromisoformat(str(first_payment).replace("Z", "+00:00"))
                    months = (datetime.now(timezone.utc) - first_date).days / 30
                    relationship_score = min(100, int(months * 8))  # Cap at 100
                except:
                    relationship_score = 50
            else:
                relationship_score = 0
            
            # Recent trend score (0-100 points) - check last 3 months
            three_months_ago = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            recent_payments = await db.payments.find({
                "buyer_id": buyer_id,
                "company_id": company_id,
                "created_at": {"$gte": three_months_ago}
            }, {"_id": 0, "status": 1}).to_list(50)
            
            if recent_payments:
                recent_on_time = len([p for p in recent_payments if p.get("status") in ["paid", "on_time", "received", "completed"]])
                recent_rate = recent_on_time / len(recent_payments)
                # Compare to overall - bonus for improving
                trend_bonus = 50 + int((recent_rate - on_time_rate) * 100)
                trend_score = max(0, min(100, trend_bonus))
            else:
                trend_score = 50
            
            # Total score (300-1000 scale, normalized to 300-850)
            raw_score = 300 + timeliness_score + volume_score + reliability_score + relationship_score + trend_score
            credit_score = min(850, max(300, int(raw_score * 0.55)))  # Scale to 300-850
            
            # Determine risk level
            if credit_score >= 750:
                risk_level = "low"
                recommendation = "Excellent payment history. Safe to extend standard credit terms."
            elif credit_score >= 650:
                risk_level = "medium"
                recommendation = "Good payment history. Consider standard credit with monitoring."
            elif credit_score >= 550:
                risk_level = "elevated"
                recommendation = "Mixed payment history. Recommend partial advance payment."
            else:
                risk_level = "high"
                recommendation = "Poor payment history. Recommend full advance payment or LC."
            
            score_data = {
                "buyer_id": buyer_id,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "payment_history": {
                    "on_time": metrics.get("on_time_count", 0),
                    "delayed": metrics.get("delayed_count", 0),
                    "total": total_payments
                },
                "score_components": {
                    "timeliness": {"score": timeliness_score, "max": 400, "weight": "40%"},
                    "volume": {"score": volume_score, "max": 200, "weight": "20%"},
                    "reliability": {"score": reliability_score, "max": 200, "weight": "20%"},
                    "relationship": {"score": relationship_score, "max": 100, "weight": "10%"},
                    "trend": {"score": trend_score, "max": 100, "weight": "10%"}
                },
                "total_transacted": metrics.get("total_amount", 0),
                "avg_transaction": metrics.get("avg_amount", 0),
                "recommendation": recommendation,
                "scoring_basis": "aggregation"
            }
        
        # Store score for audit
        score_record = {
            "id": scoring_id,
            "score_type": "buyer",
            "entity_id": buyer_id,
            "company_id": company_id,
            "user_id": user_id,
            **score_data,
            "created_at": now_iso()
        }
        await db.credit_scores.insert_one(score_record)
        
        # Audit log
        await db.audit_logs.insert_one({
            "id": generate_id(),
            "action_type": "credit_score_lookup",
            "resource_type": "buyer_score",
            "resource_id": scoring_id,
            "company_id": company_id,
            "user_id": user_id,
            "details": {
                "buyer_id": buyer_id,
                "credit_score": score_data.get("credit_score"),
                "risk_level": score_data.get("risk_level")
            },
            "timestamp": now_iso()
        })
        
        score_data["scoring_id"] = scoring_id
        return score_data
    
    @staticmethod
    async def calculate_company_score(
        company_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate company creditworthiness score using aggregation pipeline.
        
        Scoring factors:
        - Export volume (25%)
        - Payment collection rate (25%)
        - Compliance record (20%)
        - Buyer diversity (15%)
        - Growth trend (15%)
        """
        scoring_id = generate_id()
        
        # Aggregate shipment metrics
        shipment_pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": None,
                "total_shipments": {"$sum": 1},
                "total_export_value": {"$sum": {"$ifNull": ["$total_value", 0]}},
                "completed_shipments": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "unique_buyers": {"$addToSet": "$buyer_name"},
                "unique_countries": {"$addToSet": "$buyer_country"},
                "first_shipment": {"$min": "$created_at"},
                "recent_value": {
                    "$sum": {
                        "$cond": [
                            {"$gte": ["$created_at", (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()]},
                            {"$ifNull": ["$total_value", 0]},
                            0
                        ]
                    }
                }
            }},
            {"$project": {
                "total_shipments": 1,
                "total_export_value": 1,
                "completed_shipments": 1,
                "buyer_count": {"$size": "$unique_buyers"},
                "country_count": {"$size": "$unique_countries"},
                "first_shipment": 1,
                "recent_value": 1
            }}
        ]
        
        # Aggregate payment collection metrics
        payment_pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": None,
                "total_payments": {"$sum": 1},
                "total_collected": {"$sum": {"$ifNull": ["$amount", 0]}},
                "received_count": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["paid", "received", "completed"]]},
                            1,
                            0
                        ]
                    }
                }
            }}
        ]
        
        # Execute aggregations
        shipment_result = await db.shipments.aggregate(shipment_pipeline).to_list(1)
        payment_result = await db.payments.aggregate(payment_pipeline).to_list(1)
        
        ship_metrics = shipment_result[0] if shipment_result else {}
        pay_metrics = payment_result[0] if payment_result else {}
        
        # Calculate component scores
        
        # Export volume score (0-250)
        export_value = ship_metrics.get("total_export_value", 0)
        if export_value >= 10000000:  # 1 Cr+
            volume_score = 250
        elif export_value >= 5000000:  # 50L+
            volume_score = 200
        elif export_value >= 1000000:  # 10L+
            volume_score = 150
        elif export_value >= 100000:  # 1L+
            volume_score = 100
        else:
            volume_score = max(25, int(export_value / 4000))
        
        # Payment collection score (0-250)
        total_payments = pay_metrics.get("total_payments", 0)
        received_count = pay_metrics.get("received_count", 0)
        collection_rate = received_count / total_payments if total_payments > 0 else 0
        collection_score = int(collection_rate * 250)
        
        # Compliance score (0-200) - based on completed shipments ratio
        total_shipments = ship_metrics.get("total_shipments", 0)
        completed = ship_metrics.get("completed_shipments", 0)
        completion_rate = completed / total_shipments if total_shipments > 0 else 0
        compliance_score = int(completion_rate * 200)
        
        # Buyer diversity score (0-150)
        buyer_count = ship_metrics.get("buyer_count", 0)
        country_count = ship_metrics.get("country_count", 0)
        diversity_score = min(150, buyer_count * 15 + country_count * 20)
        
        # Growth trend score (0-150)
        recent_value = ship_metrics.get("recent_value", 0)
        older_value = export_value - recent_value
        if older_value > 0:
            growth_rate = (recent_value / older_value) - 1
            growth_score = min(150, max(0, int(75 + growth_rate * 75)))
        else:
            growth_score = 100 if recent_value > 0 else 50
        
        # Calculate total score (scale to 300-850)
        raw_score = volume_score + collection_score + compliance_score + diversity_score + growth_score
        company_score = min(850, max(300, int(300 + raw_score * 0.55)))
        
        # Credit limit calculation
        credit_limit = min(export_value * 0.5, 50000000)  # 50% of export value, max 5Cr
        
        # Generate recommendations
        recommendations = []
        if collection_rate < 0.8:
            recommendations.append("Improve payment collection - consider stricter terms")
        if buyer_count < 5:
            recommendations.append("Diversify buyer base to reduce concentration risk")
        if country_count < 3:
            recommendations.append("Expand to more export markets")
        if growth_score < 75:
            recommendations.append("Focus on export volume growth")
        
        if company_score >= 750:
            recommendations.insert(0, "Excellent profile - apply for enhanced credit facilities")
        elif company_score >= 650:
            recommendations.insert(0, "Good standing - eligible for standard export credit")
        
        score_data = {
            "company_score": company_score,
            "factors": {
                "export_volume": {"score": volume_score, "max": 250, "trend": "up" if growth_score > 75 else "stable"},
                "payment_collection": {"score": collection_score, "max": 250, "rate": f"{collection_rate*100:.1f}%"},
                "compliance_history": {"score": compliance_score, "max": 200, "completion_rate": f"{completion_rate*100:.1f}%"},
                "buyer_diversity": {"score": diversity_score, "max": 150, "buyers": buyer_count, "countries": country_count}
            },
            "total_export_value": export_value,
            "credit_limit_eligible": credit_limit,
            "recommendations": recommendations,
            "scoring_basis": "aggregation"
        }
        
        # Store score
        score_record = {
            "id": scoring_id,
            "score_type": "company",
            "entity_id": company_id,
            "company_id": company_id,
            "user_id": user_id,
            **score_data,
            "created_at": now_iso()
        }
        await db.credit_scores.insert_one(score_record)
        
        # Audit log
        await db.audit_logs.insert_one({
            "id": generate_id(),
            "action_type": "credit_score_lookup",
            "resource_type": "company_score",
            "resource_id": scoring_id,
            "company_id": company_id,
            "user_id": user_id,
            "details": {
                "company_score": company_score,
                "credit_limit": credit_limit
            },
            "timestamp": now_iso()
        })
        
        score_data["scoring_id"] = scoring_id
        return score_data
    
    @staticmethod
    async def get_payment_behavior_analysis(
        company_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze payment behavior patterns using aggregation.
        """
        # Regional payment analysis
        pipeline = [
            {"$match": {"company_id": company_id}},
            {"$lookup": {
                "from": "shipments",
                "localField": "shipment_id",
                "foreignField": "id",
                "as": "shipment"
            }},
            {"$unwind": {"path": "$shipment", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {"$ifNull": ["$shipment.buyer_country", "Unknown"]},
                "total_payments": {"$sum": 1},
                "total_amount": {"$sum": {"$ifNull": ["$amount", 0]}},
                "on_time_count": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["paid", "on_time", "received", "completed"]]},
                            1,
                            0
                        ]
                    }
                },
                "avg_days": {"$avg": {"$ifNull": ["$days_to_payment", 45]}}
            }},
            {"$project": {
                "region": "$_id",
                "total_payments": 1,
                "total_amount": 1,
                "on_time_rate": {
                    "$cond": [
                        {"$gt": ["$total_payments", 0]},
                        {"$multiply": [{"$divide": ["$on_time_count", "$total_payments"]}, 100]},
                        0
                    ]
                },
                "avg_days": {"$round": ["$avg_days", 0]}
            }}
        ]
        
        regional_data = await db.payments.aggregate(pipeline).to_list(50)
        
        # Overall metrics
        overall_pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": None,
                "total_payments": {"$sum": 1},
                "total_on_time": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["paid", "on_time", "received", "completed"]]},
                            1,
                            0
                        ]
                    }
                },
                "avg_collection_days": {"$avg": {"$ifNull": ["$days_to_payment", 45]}}
            }}
        ]
        
        overall = await db.payments.aggregate(overall_pipeline).to_list(1)
        overall_metrics = overall[0] if overall else {}
        
        total = overall_metrics.get("total_payments", 0)
        on_time = overall_metrics.get("total_on_time", 0)
        
        # Format regional data
        by_region = {}
        for r in regional_data:
            region = r.get("region", "Unknown")
            by_region[region] = {
                "avg_days": int(r.get("avg_days", 45)),
                "on_time": int(r.get("on_time_rate", 0)),
                "transactions": r.get("total_payments", 0)
            }
        
        return {
            "average_collection_days": int(overall_metrics.get("avg_collection_days", 45)),
            "on_time_percentage": int((on_time / total * 100) if total > 0 else 0),
            "total_transactions": total,
            "trend": "improving" if total > 10 and on_time / total > 0.7 else "stable",
            "by_region": by_region,
            "analysis_basis": "aggregation"
        }
