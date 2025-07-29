package com.taba.lawro.navigation.settings.itemscreens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.foundation.Image
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.colorResource
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.taba.lawro.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppInfoScreen(
    navController: androidx.navigation.NavController? = null
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 상단 바
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 0.dp, bottom = 16.dp)
        ) {
            // 뒤로가기 버튼
            IconButton(
                onClick = { navController?.popBackStack() },
                modifier = Modifier
                    .padding(start = 16.dp)
                    .size(48.dp)
                    .align(Alignment.CenterStart)
            ) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_back),
                    contentDescription = stringResource(R.string.back),
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(32.dp)
                )
            }
        }

        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 로고
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.symbol_logo_blue),
                        contentDescription = "symbol_logo_blue",
                        modifier = Modifier
                            .size(180.dp)
                            .align(Alignment.TopCenter)
                            .padding(bottom = 26.dp)
                    )
                    Image(
                        painter = painterResource(id = R.drawable.typo_logo_blue),
                        contentDescription = "typo_logo_blue",
                        modifier = Modifier
                            .size(180.dp)
                            .align(Alignment.BottomCenter)
                            .padding(top = 68.dp)
                            .offset(y = 8.dp)
                    )
                }
            }
        }

        // App Description
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = stringResource(R.string.app_intro_title),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                Text(
                    text = stringResource(R.string.app_intro_subtitle),
                    style = MaterialTheme.typography.titleMedium,
                    color =  colorResource(id = R.color.lawro_blue),
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                Text(
                    text = stringResource(R.string.app_intro_description),
                    style = MaterialTheme.typography.bodyMedium,
                    lineHeight = 20.sp
                )
            }
        }

        // Features Section
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = stringResource(R.string.main_features),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                
                FeatureItemWithDrawable(
                    iconResId = R.drawable.ic_analyze_selected,
                    title = stringResource(R.string.feature_contract_analysis),
                    description = stringResource(R.string.feature_contract_analysis_desc)
                )
                
                FeatureItemWithDrawable(
                    iconResId = R.drawable.select_language_logo,
                    title = stringResource(R.string.feature_multilingual_support),
                    description = stringResource(R.string.feature_multilingual_support_desc)
                )
                
                FeatureItemWithDrawable(
                    iconResId = R.drawable.ic_history_selected,
                    title = stringResource(R.string.feature_contract_history),
                    description = stringResource(R.string.feature_contract_history_desc)
                )
                
                FeatureItemWithDrawable(
                    iconResId = R.drawable.ic_chatbot_selected,
                    title = stringResource(R.string.feature_chatbot_consultation),
                    description = stringResource(R.string.feature_chatbot_consultation_desc)
                )
                
                FeatureItemWithDrawable(
                    iconResId = R.drawable.ic_worktime_selected,
                    title = stringResource(R.string.feature_worktime_tracking),
                    description = stringResource(R.string.feature_worktime_tracking_desc)
                )
                
                FeatureItem(
                    icon = Icons.Default.Language,
                    title = stringResource(R.string.feature_multilingual_ui),
                    description = stringResource(R.string.feature_multilingual_ui_desc),
                    isLast = true
                )
            }
        }

        // Developer Info
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = stringResource(R.string.developer_info),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                InfoRow(label = stringResource(R.string.development_team), value = stringResource(R.string.team_name))
                InfoRowWithLargeText(label = stringResource(R.string.supported_languages), value = stringResource(R.string.supported_languages_flags))
            }
        }

        // Copyright
        Text(
            text = stringResource(R.string.copyright),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(top = 16.dp)
        )

        Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun FeatureItem(
    icon: ImageVector,
    title: String,
    description: String,
    isLast: Boolean = false,
    descriptionStartPadding: Int = 0
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 4.dp,bottom = if (isLast) 0.dp else 16.dp),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier
                .size(24.dp),
            tint = colorResource(id = R.color.lawro_blue)
        )
        
        Spacer(modifier = Modifier.width(16.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 4.dp)
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                lineHeight = 16.sp,
                modifier = Modifier.padding(start = descriptionStartPadding.dp)
            )
        }
    }
}

@Composable
private fun FeatureItemWithDrawable(
    iconResId: Int,
    title: String,
    description: String,
    isLast: Boolean = false
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = if (isLast) 0.dp else 16.dp),
        verticalAlignment = Alignment.Top
    ) {
        Image(
            painter = painterResource(id = iconResId),
            contentDescription = null,
            modifier = Modifier
                .size(32.dp)
                .padding(top = 2.dp)
        )
        
        Spacer(modifier = Modifier.width(12.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 4.dp)
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                lineHeight = 16.sp
            )
        }
    }
}

@Composable
private fun InfoRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun InfoRowWithLargeText(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Medium
        )
    }
}