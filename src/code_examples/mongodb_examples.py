"""
MongoDB-specific code examples for RAG/KG population.

WHY:
MongoDB examples demonstrate aggregation pipelines and document-oriented patterns
that enable efficient analytics and data transformations at the database level.

RESPONSIBILITY:
- Provide MongoDB aggregation pipeline examples
- Demonstrate complex data transformations using MongoDB operators
- Show best practices for joins ($lookup) and grouping in NoSQL
- Include index creation for query optimization

PATTERNS:
- Focus on aggregation pipeline stages ($match, $group, $lookup, $unwind)
- Demonstrate MongoDB-specific operators and expressions
- Show multi-facet aggregations for efficient multi-query operations
- Include realistic e-commerce analytics use cases
"""

from code_example_types import CodeExample


MONGODB_EXAMPLES = [
    CodeExample(
        language="JavaScript",
        pattern="MongoDB Aggregation Pipeline",
        title="E-commerce Analytics with Aggregation Pipeline",
        description="Using MongoDB aggregation pipeline for complex analytics instead of MapReduce",
        code='''// MongoDB Aggregation Pipeline for Order Analytics
// Why: Complex transformations in database, not application code
// Prevents: N+1 queries, application-side joins, slow queries

// Collection: orders
/*
{
  "_id": ObjectId(),
  "userId": ObjectId(),
  "items": [
    { "productId": ObjectId(), "quantity": 2, "price": 29.99 },
    { "productId": ObjectId(), "quantity": 1, "price": 49.99 }
  ],
  "total": 109.97,
  "status": "completed",
  "createdAt": ISODate("2025-01-15")
}
*/

// Aggregation: Top selling products with revenue
db.orders.aggregate([
    // Stage 1: Filter completed orders
    {
        $match: {
            status: "completed",
            createdAt: {
                $gte: ISODate("2025-01-01"),
                $lt: ISODate("2025-02-01")
            }
        }
    },

    // Stage 2: Unwind items array (one document per item)
    { $unwind: "$items" },

    // Stage 3: Group by product, calculate metrics
    {
        $group: {
            _id: "$items.productId",
            totalQuantity: { $sum: "$items.quantity" },
            totalRevenue: {
                $sum: {
                    $multiply: ["$items.quantity", "$items.price"]
                }
            },
            orderCount: { $sum: 1 },
            avgQuantity: { $avg: "$items.quantity" }
        }
    },

    // Stage 4: Lookup product details (left join)
    {
        $lookup: {
            from: "products",
            localField: "_id",
            foreignField: "_id",
            as: "product"
        }
    },

    // Stage 5: Unwind product array (single product per document)
    { $unwind: "$product" },

    // Stage 6: Project final shape
    {
        $project: {
            _id: 0,
            productId: "$_id",
            productName: "$product.name",
            category: "$product.category",
            totalQuantity: 1,
            totalRevenue: { $round: ["$totalRevenue", 2] },
            orderCount: 1,
            avgQuantity: { $round: ["$avgQuantity", 2] },
            revenuePerOrder: {
                $round: [
                    { $divide: ["$totalRevenue", "$orderCount"] },
                    2
                ]
            }
        }
    },

    // Stage 7: Sort by revenue (descending)
    { $sort: { totalRevenue: -1 } },

    // Stage 8: Limit to top 10
    { $limit: 10 },

    // Stage 9: Add computed fields
    {
        $addFields: {
            rank: { $add: [{ $indexOfArray: ["$$ROOT", "$$ROOT"] }, 1] }
        }
    }
]);

// User purchase behavior analysis
db.orders.aggregate([
    {
        $match: { status: "completed" }
    },
    {
        $group: {
            _id: "$userId",
            totalOrders: { $sum: 1 },
            totalSpent: { $sum: "$total" },
            avgOrderValue: { $avg: "$total" },
            firstPurchase: { $min: "$createdAt" },
            lastPurchase: { $max: "$createdAt" }
        }
    },
    {
        $project: {
            userId: "$_id",
            _id: 0,
            totalOrders: 1,
            totalSpent: { $round: ["$totalSpent", 2] },
            avgOrderValue: { $round: ["$avgOrderValue", 2] },
            firstPurchase: 1,
            lastPurchase: 1,
            daysSinceFirst: {
                $divide: [
                    { $subtract: ["$lastPurchase", "$firstPurchase"] },
                    86400000  // milliseconds in a day
                ]
            },
            customerSegment: {
                $switch: {
                    branches: [
                        { case: { $gte: ["$totalSpent", 1000] }, then: "VIP" },
                        { case: { $gte: ["$totalSpent", 500] }, then: "Premium" },
                        { case: { $gte: ["$totalSpent", 100] }, then: "Regular" }
                    ],
                    default: "New"
                }
            }
        }
    },
    {
        $sort: { totalSpent: -1 }
    }
]);

// Create index for aggregation performance
db.orders.createIndex({ status: 1, createdAt: -1 });
db.orders.createIndex({ userId: 1, status: 1 });

// Use $facet for multiple aggregations in one query
db.orders.aggregate([
    {
        $facet: {
            // Facet 1: Revenue by status
            byStatus: [
                {
                    $group: {
                        _id: "$status",
                        totalRevenue: { $sum: "$total" },
                        count: { $sum: 1 }
                    }
                }
            ],
            // Facet 2: Revenue by month
            byMonth: [
                {
                    $group: {
                        _id: {
                            $dateToString: {
                                format: "%Y-%m",
                                date: "$createdAt"
                            }
                        },
                        totalRevenue: { $sum: "$total" },
                        count: { $sum: 1 }
                    }
                },
                { $sort: { _id: 1 } }
            ],
            // Facet 3: Overall stats
            overall: [
                {
                    $group: {
                        _id: null,
                        totalRevenue: { $sum: "$total" },
                        totalOrders: { $sum: 1 },
                        avgOrderValue: { $avg: "$total" }
                    }
                }
            ]
        }
    }
]);
''',
        quality_score=95,
        tags=["MongoDB", "aggregation-pipeline", "analytics", "lookup", "facets"],
        complexity="advanced",
        demonstrates=["Aggregation Pipeline", "$lookup", "$unwind", "$facet", "Complex Grouping"],
        prevents=["N+1 Queries", "Application-Side Joins", "MapReduce"]
    ),
]
