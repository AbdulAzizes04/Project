const axios = require('axios');

/**
 * AI Service to handle Query Spec generation and conversational responses.
 */
class LLMService {
  /**
   * Generates a Pandas Query Spec from the user's natural language query.
   * Query Spec structure:
   * {
   *   "action": "groupby" | "trend" | "correlation" | "top_records" | "stats",
   *   "groupby_col": "...",
   *   "target_col": "...",
   *   "agg": "sum" | "mean" | "count" | "min" | "max",
   *   "date_col": "...",
   *   "freq": "ME" | "D",
   *   "filters": [{"col": "...", "op": "==", "val": "..."}]
   * }
   */
  static async generateQuerySpec(userQuery, datasetMetadata, chatHistory = []) {
    const geminiKey = process.env.GEMINI_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    // Format recent chat history (e.g., last 6 messages) for context
    const historyText = chatHistory.slice(-6).map(m => `${m.role.toUpperCase()}: ${m.content}`).join('\n');
    
    const columnsText = datasetMetadata.columns.map(c => `- ${c.name} (${c.type})`).join('\n');
    const prompt = `You are a data analyst. Given a dataset schema and recent chat history, translate the user's latest natural language query into a structured JSON query specification.
    
Dataset Columns:
${columnsText}

Recent Chat History:
${historyText || 'No previous conversation history.'}

Latest User Query: "${userQuery}"

JSON Query Spec Schema:
{
  "action": "groupby" | "trend" | "correlation" | "top_records" | "stats",
  "groupby_col": "string (required for groupby)",
  "target_col": "string (required for groupby, trend, correlation, stats)",
  "agg": "sum" | "mean" | "count" | "min" | "max" (default: "sum"),
  "date_col": "string (required for trend)",
  "freq": "ME" | "D" | "YE" (default: "ME" for month-end),
  "col1": "string (required for correlation)",
  "col2": "string (required for correlation)",
  "sort_by": "string (required for top_records)",
  "limit": number (for top_records),
  "ascending": boolean (default: false),
  "filters": [
    {
      "col": "string",
      "op": "==" | "!=" | ">" | "<" | ">=" | "<=" | "contains",
      "val": any
    }
  ]
}

Instructions:
1. Return ONLY a valid JSON object matching the schema. No markdown formatting, no comments, no enclosing code blocks.
2. Select the single action that best fits the query.
3. Match column names EXACTLY.
4. If the query asks for a trend or overtime analysis, set action="trend" and identify the datetime column as date_col.
5. If the query asks for segmentations/breakdowns, set action="groupby".
6. If the query asks for descriptive stats (e.g. total, average, max of a column), set action="stats".
7. If no action fits, set action="stats" with the target_col being the most relevant numeric column.`;

    if (geminiKey) {
      try {
        const response = await axios.post(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiKey}`,
          {
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { responseMimeType: "application/json" }
          }
        );
        const text = response.data.candidates[0].content.parts[0].text;
        return JSON.parse(text);
      } catch (err) {
        console.error('Gemini query spec generation error, falling back to rule-based parser:', err.message);
      }
    } else if (openAIKey) {
      try {
        const response = await axios.post(
          'https://api.openai.com/v1/chat/completions',
          {
            model: 'gpt-4o-mini',
            messages: [
              { role: 'system', content: 'You only output valid JSON representing a pandas query spec.' },
              { role: 'user', content: prompt }
            ],
            response_format: { type: "json_object" }
          },
          { headers: { Authorization: `Bearer ${openAIKey}` } }
        );
        const text = response.data.choices[0].message.content;
        return JSON.parse(text);
      } catch (err) {
        console.error('OpenAI query spec generation error, falling back to rule-based parser:', err.message);
      }
    }

    // Fallback: Rule-Based Parser (Keyword Matcher)
    return this.ruleBasedQuerySpec(userQuery, datasetMetadata);
  }

  static ruleBasedQuerySpec(userQuery, datasetMetadata) {
    const q = userQuery.toLowerCase();
    const cols = datasetMetadata.columns;
    
    // Find numeric and date columns
    const numericCols = cols.filter(c => c.type === 'numeric').map(c => c.name);
    const dateCols = cols.filter(c => c.type === 'datetime').map(c => c.name);
    const catCols = cols.filter(c => c.type === 'categorical').map(c => c.name);

    // Let's identify targets and group-bys
    let target_col = numericCols[0] || '';
    for (let c of numericCols) {
      if (q.includes(c.toLowerCase())) {
        target_col = c;
        break;
      }
    }
    
    let groupby_col = catCols[0] || '';
    for (let c of catCols) {
      if (q.includes(c.toLowerCase())) {
        groupby_col = c;
        break;
      }
    }

    let date_col = dateCols[0] || '';
    for (let c of dateCols) {
      if (q.includes(c.toLowerCase())) {
        date_col = c;
        break;
      }
    }

    // Determine Action
    if (q.includes('trend') || q.includes('over time') || q.includes('monthly') || q.includes('daily') || q.includes('forecast')) {
      if (date_col && target_col) {
        return { action: 'trend', date_col, target_col, freq: 'ME' };
      }
    }

    if (q.includes('correlation') || q.includes('correlate') || q.includes('relationship')) {
      if (numericCols.length >= 2) {
        return {
          action: 'correlation',
          col1: numericCols[0],
          col2: numericCols[1]
        };
      }
    }

    if (q.includes('highest') || q.includes('best') || q.includes('top') || q.includes('lowest') || q.includes('worst')) {
      if (groupby_col && target_col) {
        return {
          action: 'groupby',
          groupby_col,
          target_col,
          agg: 'sum',
          ascending: q.includes('lowest') || q.includes('worst')
        };
      }
      if (target_col) {
        return {
          action: 'top_records',
          sort_by: target_col,
          limit: 5,
          ascending: q.includes('lowest') || q.includes('worst')
        };
      }
    }

    if (groupby_col && target_col) {
      return { action: 'groupby', groupby_col, target_col, agg: 'sum' };
    }

    if (target_col) {
      return { action: 'stats', target_col };
    }

    return { action: 'stats', target_col: cols[0].name };
  }

  /**
   * Generates a final conversational answer based on user query and query results.
   */
  static async generateAnswer(userQuery, querySpec, queryResults, datasetMetadata, chatHistory = []) {
    const geminiKey = process.env.GEMINI_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;

    // Format recent chat history (e.g., last 6 messages) for context
    const historyText = chatHistory.slice(-6).map(m => `${m.role === 'assistant' ? 'AI' : 'User'}: ${m.content}`).join('\n');

    const prompt = `You are a high-level Business AI Advisor. Answer the user's business question using the provided dataset query results and dataset metadata.

Dataset Context:
- Dataset Name: ${datasetMetadata.name}
- Row Count: ${datasetMetadata.rowCount}
- Column Count: ${datasetMetadata.columnCount}

Query Run:
- Action: ${querySpec.action}
- Target Column: ${querySpec.target_col || 'N/A'}
- GroupBy Column: ${querySpec.groupby_col || 'N/A'}

Query Results:
${JSON.stringify(queryResults, null, 2)}

Recent Conversation History:
${historyText || 'No previous conversation.'}

User Question: "${userQuery}"

Provide a professional, clear, data-driven answer. 
Guidelines:
1. Explain the results clearly in business terms. Include numbers, percentages, and comparisons if applicable.
2. If there are trends, explain if they are positive, negative, or seasonal.
3. Provide 2-3 actionable business recommendations based on this analysis.
4. Keep the answer structured using markdown (e.g. headers, bold text, bullet points).
5. If the results are empty, explain that no matching records were found for the query filters.`;

    if (geminiKey) {
      try {
        const response = await axios.post(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiKey}`,
          {
            contents: [{ parts: [{ text: prompt }] }]
          }
        );
        return response.data.candidates[0].content.parts[0].text;
      } catch (err) {
        console.error('Gemini answer generation error, falling back to rule-based response:', err.message);
      }
    } else if (openAIKey) {
      try {
        const response = await axios.post(
          'https://api.openai.com/v1/chat/completions',
          {
            model: 'gpt-4o-mini',
            messages: [
              { role: 'system', content: 'You are a helpful business analytics advisor.' },
              { role: 'user', content: prompt }
            ]
          },
          { headers: { Authorization: `Bearer ${openAIKey}` } }
        );
        return response.data.choices[0].message.content;
      } catch (err) {
        console.error('OpenAI answer generation error, falling back to rule-based response:', err.message);
      }
    }

    // Fallback: Rule-Based Conversational Engine
    return this.ruleBasedAnswer(userQuery, querySpec, queryResults);
  }

  static ruleBasedAnswer(userQuery, querySpec, queryResults) {
    let responseText = `### Business Advisory Summary\n\n`;
    responseText += `*Analysis performed on dataset using **${querySpec.action}** query.* \n\n`;

    if (!queryResults || (Array.isArray(queryResults) && queryResults.length === 0)) {
      responseText += `No data was returned for your query. This might be due to active filters or missing records in the columns analyzed. Please check your dataset inputs.`;
      return responseText;
    }

    if (querySpec.action === 'groupby') {
      const topRecord = queryResults[0];
      const gbCol = querySpec.groupby_col;
      const targetCol = querySpec.target_col;
      
      responseText += `Based on the breakdown of **${targetCol}** by **${gbCol}**:\n`;
      responseText += `- The highest performing category is **${topRecord[gbCol]}** with a total of **${Number(topRecord[targetCol]).toLocaleString(undefined, {maximumFractionDigits: 2})}**.\n`;
      
      if (queryResults.length > 1) {
        const lastRecord = queryResults[queryResults.length - 1];
        responseText += `- The lowest performing category is **${lastRecord[gbCol]}** with a total of **${Number(lastRecord[targetCol]).toLocaleString(undefined, {maximumFractionDigits: 2})}**.\n\n`;
      }

      responseText += `#### Top Categories Breakdown:\n`;
      queryResults.slice(0, 5).forEach((row, i) => {
        responseText += `${i + 1}. **${row[gbCol]}**: ${Number(row[targetCol]).toLocaleString(undefined, {maximumFractionDigits: 2})}\n`;
      });

      responseText += `\n#### Business Recommendations:\n`;
      responseText += `- **Optimize Resource Allocation**: Focus marketing and operational resources on **${topRecord[gbCol]}** to capitalize on its high yield.\n`;
      responseText += `- **Review Low Performers**: Investigate underperforming categories to see if there is potential for price adjustments or restructuring.`;

    } else if (querySpec.action === 'trend') {
      const dateCol = querySpec.date_col;
      const targetCol = querySpec.target_col;
      
      responseText += `Based on the temporal analysis of **${targetCol}** over time:\n`;
      responseText += `- Total records tracked: **${queryResults.length} periods**.\n`;
      
      const first = queryResults[0];
      const last = queryResults[queryResults.length - 1];
      const trendDir = Number(last[targetCol]) >= Number(first[targetCol]) ? 'an upward' : 'a downward';
      
      responseText += `- The trend moved from **${Number(first[targetCol]).toLocaleString(undefined, {maximumFractionDigits: 2})}** (at ${first[dateCol]}) to **${Number(last[targetCol]).toLocaleString(undefined, {maximumFractionDigits: 2})}** (at ${last[dateCol]}), representing **${trendDir}** direction.\n\n`;

      responseText += `#### Actionable Recommendations:\n`;
      responseText += `- **Sales Forecasting**: Prepare stock and inventory levels aligned with the observed temporal fluctuations.\n`;
      responseText += `- **Seasonal Strategy**: Leverage peak months to run high-impact campaigns, and offer promotions during low-performing periods.`;

    } else if (querySpec.action === 'stats') {
      const targetCol = querySpec.target_col;
      responseText += `#### Statistical Summary for ${targetCol}:\n`;
      if (queryResults.mean !== undefined) {
        responseText += `- **Total Sum**: ${Number(queryResults.sum).toLocaleString(undefined, {maximumFractionDigits: 2})}\n`;
        responseText += `- **Average (Mean)**: ${Number(queryResults.mean).toLocaleString(undefined, {maximumFractionDigits: 2})}\n`;
        responseText += `- **Minimum**: ${Number(queryResults.min).toLocaleString(undefined, {maximumFractionDigits: 2})}\n`;
        responseText += `- **Maximum**: ${Number(queryResults.max).toLocaleString(undefined, {maximumFractionDigits: 2})}\n`;
        responseText += `- **Count**: ${queryResults.count}\n\n`;
      } else {
        responseText += `- **Total Count**: ${queryResults.count}\n`;
        responseText += `- **Unique Values**: ${queryResults.unique}\n`;
        responseText += `- **Top Categories**:\n`;
        for (let key in queryResults.top_values) {
          responseText += `  - **${key}**: ${queryResults.top_values[key]} records\n`;
        }
        responseText += `\n`;
      }
      responseText += `#### Actionable Recommendations:\n`;
      responseText += `- **Performance Tracking**: Use these baseline averages as benchmarks for setting upcoming business targets.\n`;
      responseText += `- **Outlier Investigation**: Verify whether the maximum outlier values represent regular high-value clients or anomalies.`;
    } else if (querySpec.action === 'correlation') {
      const corr = queryResults.correlation;
      let strength = 'very weak';
      if (Math.abs(corr) > 0.7) strength = 'strong';
      else if (Math.abs(corr) > 0.4) strength = 'moderate';
      
      responseText += `Correlation between variables analyzed is **${corr.toFixed(3)}**, indicating a **${strength}** relationship.\n\n`;
      responseText += `#### Actionable Recommendations:\n`;
      if (Math.abs(corr) > 0.4) {
        responseText += `- **Leverage Dependency**: Since these features are correlated, changes in one can be used to predict the other. Adjust strategic forecasts accordingly.`;
      } else {
        responseText += `- **Isolate Factors**: These variables behave independently. Avoid assuming that changes in one will influence the other in operations.`;
      }
    } else {
      responseText += `General analysis results:\n\`\`\`json\n${JSON.stringify(queryResults, null, 2)}\n\`\`\``;
    }

    return responseText;
  }

  /**
   * Generates executive summary and recommendations for the PDF report.
   */
  static async generateReportInsights(datasetMetadata, mlModels = []) {
    const geminiKey = process.env.GEMINI_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;

    // Generate detailed textual overview of columns
    const columnsSummaryText = datasetMetadata.columns.map(c => {
      let text = `- **${c.name}** (${c.type}): ${c.nullCount} nulls, ${c.uniqueCount} unique values.`;
      if (c.type === 'numeric' && c.stats) {
        text += ` Stats: Mean=${Number(c.stats.mean).toFixed(2)}, Median=${Number(c.stats.median).toFixed(2)}, Min=${Number(c.stats.min).toFixed(2)}, Max=${Number(c.stats.max).toFixed(2)}`;
      } else if (c.type === 'categorical' && c.stats && c.stats.top_values) {
        const top = Object.entries(c.stats.top_values).slice(0, 2).map(([k, v]) => `"${k}" (${v} times)`).join(', ');
        text += ` Top Values: ${top}`;
      }
      return text;
    }).join('\n');

    const prompt = `You are a Principal Enterprise Consultant. Write a high-level executive summary and set of strategic recommendations for a business dataset report.
    
Dataset Summary:
- Name: ${datasetMetadata.name}
- Rows: ${datasetMetadata.rowCount}
- Columns: ${datasetMetadata.columnCount}
- Duplicates: ${datasetMetadata.summary?.duplicates || 0}
- Suggested KPIs: ${JSON.stringify(datasetMetadata.summary?.suggestedKPIs || [])}

Columns & Distribution Statistics:
${columnsSummaryText}

Trained Machine Learning Models:
${JSON.stringify(mlModels.map(m => ({ taskType: m.taskType, target: m.targetVariable, metrics: m.metrics })), null, 2)}

Provide the report contents in exactly two parts, styled with markdown:
1. EXECUTIVE SUMMARY: A detailed, data-driven paragraph analyzing the specific metrics, columns, and general health of the business based on the KPIs.
2. STRATEGIC RECOMMENDATIONS: 4 bullet points outlining key strategies the company should execute, directly referencing the column insights and metrics.`;

    if (geminiKey) {
      try {
        const response = await axios.post(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiKey}`,
          { contents: [{ parts: [{ text: prompt }] }] }
        );
        return response.data.candidates[0].content.parts[0].text;
      } catch (err) {
        console.error('Gemini report insights error:', err.message);
      }
    } else if (openAIKey) {
      try {
        const response = await axios.post(
          'https://api.openai.com/v1/chat/completions',
          {
            model: 'gpt-4o-mini',
            messages: [{ role: 'user', content: prompt }]
          },
          { headers: { Authorization: `Bearer ${openAIKey}` } }
        );
        return response.data.choices[0].message.content;
      } catch (err) {
        console.error('OpenAI report insights error:', err.message);
      }
    }

    // Fallback: build a dynamic data-driven summary based on the actual columns
    let summary = `### Executive Summary\n`;
    summary += `The dataset "${datasetMetadata.name}" contains ${datasetMetadata.rowCount} records across ${datasetMetadata.columnCount} columns. `;
    
    // Check duplicates and nulls
    const totalNulls = datasetMetadata.columns.reduce((sum, col) => sum + (col.nullCount || 0), 0);
    const duplicates = datasetMetadata.summary?.duplicates || 0;
    
    if (duplicates > 0 || totalNulls > 0) {
      summary += `A data quality audit detected ${duplicates} duplicate records and ${totalNulls} missing values across features. `;
    } else {
      summary += `A data quality audit confirmed high integrity with 0 duplicates and 0 missing values. `;
    }

    // Include details from suggested KPIs
    const kpis = datasetMetadata.summary?.suggestedKPIs || [];
    if (kpis.length > 0) {
      summary += `Key KPIs tracked include: ` + kpis.map(k => `**${k.column}** (Total: ${Number(k.sum).toLocaleString(undefined, {maximumFractionDigits:2})}, Average: ${Number(k.avg).toLocaleString(undefined, {maximumFractionDigits:2})})`).join(', ') + `. `;
    }

    // Look for top categories in categorical columns
    const catCols = datasetMetadata.columns.filter(c => c.type === 'categorical' && c.stats && c.stats.top_values);
    if (catCols.length > 0) {
      const topCatText = catCols.slice(0, 2).map(c => {
        const topVal = Object.keys(c.stats.top_values)[0];
        const topCount = c.stats.top_values[topVal];
        const pct = ((topCount / datasetMetadata.rowCount) * 100).toFixed(1);
        return `**${c.name}** is dominated by **${topVal}** (${pct}% frequency)`;
      }).join(', and ');
      summary += `Distribution profiling shows that ${topCatText}. `;
    }

    // Look for outliers in numeric columns
    const outliers = datasetMetadata.summary?.outliers || {};
    const outlierCols = Object.entries(outliers).filter(([_, info]) => info.outlierCount > 0);
    if (outlierCols.length > 0) {
      summary += `Statistical outlier scans identified high variance values in ` + outlierCols.map(([col, info]) => `**${col}** (${info.outlierCount} outliers, ${Number(info.percentage).toFixed(1)}% of rows)`).join(', ') + `. `;
    }

    summary += `Overall, the metrics provide a clear baseline for business profiling and predictive modeling.`;
    
    summary += `\n\n### Strategic Recommendations\n`;
    
    // Tailored recommendations
    if (kpis.length > 0) {
      summary += `- **Optimize KPI Margins**: Establish specific operational targets around **${kpis[0].column}** to capitalize on high volume sectors.\n`;
    } else {
      summary += `- **Identify Core Business Value**: Profile numeric features to target top operational drivers.\n`;
    }

    if (outlierCols.length > 0) {
      summary += `- **Mitigate Outlier Instability**: Investigate extreme values in **${outlierCols[0][0]}** to verify if they are transaction errors or ultra-high value clients.\n`;
    } else {
      summary += `- **Maintain Distribution Stability**: Keep monitoring numeric variables to detect operational drift early.\n`;
    }

    if (catCols.length > 0) {
      const firstCat = catCols[0];
      const topVal = Object.keys(firstCat.stats.top_values)[0];
      summary += `- **Target Segment Performance**: Design customized campaigns addressing the dominant **${firstCat.name}** segment (**${topVal}**).\n`;
    } else {
      summary += `- **Enhance Category Segmentation**: Group transactions to understand structural margins.\n`;
    }

    if (duplicates > 0 || totalNulls > 0) {
      summary += `- **Data Quality Rectification**: Implement automated validation workflows to deduplicate transactions and fill missing values.\n`;
    } else {
      summary += `- **Data Model Training**: Proceed to run predictive machine learning modeling (e.g. XGBoost) using the clean schema.\n`;
    }
    
    return summary;
  }
}

module.exports = LLMService;
